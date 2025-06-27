#!/usr/bin/env python3
"""
Database tests for SecRef
Tests SQLite schema, import/export functionality, and data integrity
"""

import unittest
import os
import sys
import tempfile
import shutil
import json
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.db_config_sqlite import get_db_connection
from scripts.import_json_to_sqlite import JSONImporter
from scripts.export_sqlite_to_json import JSONExporter


class TestDatabase(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Create a temporary database for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test.db')
        os.environ['SECREF_DB_PATH'] = self.db_path
        
        # Create test JSON data
        self.test_data_dir = os.path.join(self.test_dir, 'test_data')
        os.makedirs(os.path.join(self.test_data_dir, 'src', 'data', 'tools'), exist_ok=True)
        
        self.sample_data = {
            "reconnaissance": {
                "name": "Reconnaissance",
                "description": "Tools for information gathering",
                "subcategories": {
                    "port_scanners": {
                        "name": "Port Scanners",
                        "tools": [
                            {
                                "name": "Nmap",
                                "url": "https://nmap.org",
                                "description": "Network discovery and security auditing",
                                "type": "free",
                                "tags": ["network", "scanning"],
                                "platforms": ["windows", "linux", "macos"],
                                "isCommunityFavorite": True,
                                "isIndustryStandard": True
                            },
                            {
                                "name": "Masscan",
                                "url": "https://github.com/robertdavidgraham/masscan",
                                "description": "Fast port scanner",
                                "type": "free",
                                "notation": "",
                                "pricingNote": "",
                                "tags": ["network", "fast"],
                                "platforms": ["linux"]
                            }
                        ]
                    }
                }
            }
        }
        
        # Write test JSON file
        json_path = os.path.join(self.test_data_dir, 'src', 'data', 'tools', 'reconnaissance.json')
        with open(json_path, 'w') as f:
            json.dump(self.sample_data, f, indent=2)
    
    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_database_creation(self):
        """Test that database tables are created correctly"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check all tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row['name'] for row in cursor.fetchall()]
            
            expected_tables = [
                'audit_log', 'categories', 'resource_categories', 
                'resource_links', 'resource_platforms', 'resource_tags', 
                'resources'
            ]
            
            for table in expected_tables:
                self.assertIn(table, tables, f"Table {table} should exist")
    
    def test_json_import(self):
        """Test importing JSON data into database"""
        importer = JSONImporter()
        importer.import_all(self.test_data_dir)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check resources were imported
            cursor.execute("SELECT COUNT(*) as count FROM resources")
            self.assertEqual(cursor.fetchone()['count'], 2)
            
            # Check specific resource
            cursor.execute("SELECT * FROM resources WHERE name = ?", ("Nmap",))
            nmap = cursor.fetchone()
            self.assertIsNotNone(nmap)
            self.assertEqual(nmap['url'], 'https://nmap.org')
            self.assertEqual(nmap['type'], 'free')
            self.assertTrue(nmap['is_community_favorite'])
            self.assertTrue(nmap['is_industry_standard'])
            
            # Check categories
            cursor.execute("SELECT COUNT(*) as count FROM categories")
            self.assertEqual(cursor.fetchone()['count'], 2)  # reconnaissance and port_scanners
            
            # Check tags
            cursor.execute("""
                SELECT tag FROM resource_tags 
                WHERE resource_id = ?
                ORDER BY tag
            """, (nmap['id'],))
            tags = [row['tag'] for row in cursor.fetchall()]
            self.assertEqual(tags, ['network', 'scanning'])
            
            # Check platforms
            cursor.execute("""
                SELECT platform FROM resource_platforms 
                WHERE resource_id = ?
                ORDER BY platform
            """, (nmap['id'],))
            platforms = [row['platform'] for row in cursor.fetchall()]
            self.assertEqual(platforms, ['linux', 'macos', 'windows'])
    
    def test_json_export(self):
        """Test exporting database back to JSON"""
        # First import
        importer = JSONImporter()
        importer.import_all(self.test_data_dir)
        
        # Then export to a different location
        export_dir = os.path.join(self.test_dir, 'export')
        exporter = JSONExporter()
        exporter.export_all(export_dir)
        
        # Check exported file exists
        exported_file = os.path.join(export_dir, 'src', 'data', 'tools', 'reconnaissance.json')
        self.assertTrue(os.path.exists(exported_file))
        
        # Load and verify exported data
        with open(exported_file, 'r') as f:
            exported_data = json.load(f)
        
        # Check structure
        self.assertIn('reconnaissance', exported_data)
        self.assertIn('port_scanners', exported_data['reconnaissance']['subcategories'])
        
        # Check tools
        tools = exported_data['reconnaissance']['subcategories']['port_scanners']['tools']
        self.assertEqual(len(tools), 2)
        
        # Find Nmap in exported data
        nmap = next(t for t in tools if t['name'] == 'Nmap')
        self.assertEqual(nmap['url'], 'https://nmap.org')
        self.assertTrue(nmap['isCommunityFavorite'])
        self.assertTrue(nmap['isIndustryStandard'])
        self.assertEqual(set(nmap['tags']), {'network', 'scanning'})
        self.assertEqual(set(nmap['platforms']), {'windows', 'linux', 'macos'})
    
    def test_resource_crud_operations(self):
        """Test Create, Read, Update, Delete operations"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create
            resource_id = 'test-resource-123'
            cursor.execute("""
                INSERT INTO resources (id, name, slug, url, description, type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (resource_id, 'Test Tool', 'test-tool', 'https://test.com', 
                  'Test description', 'free'))
            
            # Read
            cursor.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
            resource = cursor.fetchone()
            self.assertEqual(resource['name'], 'Test Tool')
            self.assertEqual(resource['url'], 'https://test.com')
            
            # Update
            cursor.execute("""
                UPDATE resources 
                SET description = ?, is_community_favorite = 1
                WHERE id = ?
            """, ('Updated description', resource_id))
            
            cursor.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
            resource = cursor.fetchone()
            self.assertEqual(resource['description'], 'Updated description')
            self.assertTrue(resource['is_community_favorite'])
            
            # Delete
            cursor.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
            cursor.execute("SELECT COUNT(*) as count FROM resources WHERE id = ?", (resource_id,))
            self.assertEqual(cursor.fetchone()['count'], 0)
            
            conn.commit()
    
    def test_audit_log(self):
        """Test audit log functionality"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Add audit entry
            cursor.execute("""
                INSERT INTO audit_log (table_name, record_id, action, changed_by)
                VALUES ('resources', 'test-123', 'create', 'test_user')
            """)
            
            # Check audit log
            cursor.execute("""
                SELECT * FROM audit_log 
                WHERE record_id = 'test-123'
                ORDER BY changed_at DESC
            """)
            audit = cursor.fetchone()
            
            self.assertEqual(audit['table_name'], 'resources')
            self.assertEqual(audit['action'], 'create')
            self.assertEqual(audit['changed_by'], 'test_user')
            self.assertIsNotNone(audit['changed_at'])
    
    def test_category_hierarchy(self):
        """Test category parent-child relationships"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create parent category
            parent_id = 'parent-cat'
            cursor.execute("""
                INSERT INTO categories (id, name, slug, description)
                VALUES (?, ?, ?, ?)
            """, (parent_id, 'Parent Category', 'parent-category', 'Parent desc'))
            
            # Create child categories
            for i in range(3):
                cursor.execute("""
                    INSERT INTO categories (id, name, slug, parent_id, sort_order)
                    VALUES (?, ?, ?, ?, ?)
                """, (f'child-{i}', f'Child {i}', f'child-{i}', parent_id, i))
            
            # Query children
            cursor.execute("""
                SELECT * FROM categories 
                WHERE parent_id = ?
                ORDER BY sort_order
            """)
            children = cursor.fetchall()
            
            self.assertEqual(len(children), 3)
            self.assertEqual(children[0]['name'], 'Child 0')
            self.assertEqual(children[2]['sort_order'], 2)
            
            conn.commit()
    
    def test_resource_categories(self):
        """Test many-to-many resource-category relationships"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create resource and categories
            resource_id = 'res-123'
            cursor.execute("""
                INSERT INTO resources (id, name, slug)
                VALUES (?, ?, ?)
            """, (resource_id, 'Multi-category Tool', 'multi-cat'))
            
            cat_ids = []
            for i in range(3):
                cat_id = f'cat-{i}'
                cat_ids.append(cat_id)
                cursor.execute("""
                    INSERT INTO categories (id, name, slug)
                    VALUES (?, ?, ?)
                """, (cat_id, f'Category {i}', f'cat-{i}'))
            
            # Assign categories (first is primary)
            for i, cat_id in enumerate(cat_ids):
                cursor.execute("""
                    INSERT INTO resource_categories (resource_id, category_id, is_primary, sort_order)
                    VALUES (?, ?, ?, ?)
                """, (resource_id, cat_id, 1 if i == 0 else 0, i))
            
            # Query resource categories
            cursor.execute("""
                SELECT c.name, rc.is_primary
                FROM categories c
                JOIN resource_categories rc ON c.id = rc.category_id
                WHERE rc.resource_id = ?
                ORDER BY rc.sort_order
            """, (resource_id,))
            
            cats = cursor.fetchall()
            self.assertEqual(len(cats), 3)
            self.assertTrue(cats[0]['is_primary'])
            self.assertFalse(cats[1]['is_primary'])
            
            conn.commit()
    
    def test_duplicate_url_detection(self):
        """Test that duplicate URLs can be detected"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Insert two resources with same URL
            url = 'https://duplicate.com'
            cursor.execute("""
                INSERT INTO resources (id, name, slug, url)
                VALUES (?, ?, ?, ?)
            """, ('res-1', 'Tool 1', 'tool-1', url))
            
            cursor.execute("""
                INSERT INTO resources (id, name, slug, url)
                VALUES (?, ?, ?, ?)
            """, ('res-2', 'Tool 2', 'tool-2', url))
            
            # Query for duplicates
            cursor.execute("""
                SELECT url, COUNT(*) as count
                FROM resources
                WHERE url IS NOT NULL AND url != ''
                GROUP BY url
                HAVING COUNT(*) > 1
            """)
            
            duplicates = cursor.fetchall()
            self.assertEqual(len(duplicates), 1)
            self.assertEqual(duplicates[0]['url'], url)
            self.assertEqual(duplicates[0]['count'], 2)
            
            conn.commit()
    
    def test_sync_detection(self):
        """Test database/JSON sync detection logic"""
        # Import initial data
        importer = JSONImporter()
        importer.import_all(self.test_data_dir)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Add export record
            cursor.execute("""
                INSERT INTO audit_log (table_name, record_id, action, changed_by)
                VALUES ('system', 'export', 'json_export', 'test')
            """)
            
            # Make a change
            cursor.execute("""
                UPDATE resources SET description = 'Changed' WHERE name = 'Nmap'
            """)
            
            # Add update record  
            cursor.execute("""
                INSERT INTO audit_log (table_name, record_id, action, changed_by)
                VALUES ('resources', 'nmap-id', 'update', 'test')
            """)
            
            # Check for changes after last export
            cursor.execute("""
                SELECT COUNT(*) as count FROM audit_log
                WHERE action = 'update'
                AND changed_at > (
                    SELECT MAX(changed_at) FROM audit_log 
                    WHERE action = 'json_export'
                )
            """)
            
            changes = cursor.fetchone()['count']
            self.assertEqual(changes, 1)
            
            conn.commit()


if __name__ == '__main__':
    unittest.main()