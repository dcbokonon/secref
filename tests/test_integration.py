#!/usr/bin/env python3
"""
Integration tests for SecRef
Tests the full workflow from JSON import to export
"""

import unittest
import os
import sys
import tempfile
import shutil
import json
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.db_config_sqlite import get_db_connection
from scripts.import_json_to_sqlite import JSONImporter
from scripts.export_sqlite_to_json import JSONExporter
from admin.app import app


class TestIntegration(unittest.TestCase):
    """Test full system integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test.db')
        os.environ['SECREF_DB_PATH'] = self.db_path
        
        # Set up Flask test client
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Create comprehensive test data
        self.create_test_data()
    
    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_test_data(self):
        """Create comprehensive test JSON files"""
        data_dir = os.path.join(self.test_dir, 'src', 'data', 'tools')
        os.makedirs(data_dir, exist_ok=True)
        
        # Create multiple category files
        self.test_files = {
            'reconnaissance.json': {
                "reconnaissance": {
                    "name": "Reconnaissance",
                    "description": "Information gathering tools",
                    "subcategories": {
                        "port_scanners": {
                            "name": "Port Scanners",
                            "tools": [
                                {
                                    "name": "Nmap",
                                    "url": "https://nmap.org",
                                    "description": "Network exploration tool",
                                    "type": "free",
                                    "isCommunityFavorite": True,
                                    "isIndustryStandard": True,
                                    "tags": ["network", "scanning", "discovery"],
                                    "platforms": ["windows", "linux", "macos"]
                                },
                                {
                                    "name": "Masscan",
                                    "url": "https://github.com/robertdavidgraham/masscan",
                                    "description": "Fastest port scanner",
                                    "type": "free",
                                    "tags": ["network", "fast"],
                                    "platforms": ["linux"]
                                }
                            ]
                        },
                        "osint": {
                            "name": "OSINT",
                            "tools": [
                                {
                                    "name": "theHarvester",
                                    "url": "https://github.com/laramies/theHarvester",
                                    "description": "Email and subdomain harvesting",
                                    "type": "free",
                                    "tags": ["osint", "recon"],
                                    "platforms": ["linux", "macos"]
                                }
                            ]
                        }
                    }
                }
            },
            'web_security.json': {
                "web_security": {
                    "name": "Web Security",
                    "description": "Web application testing tools",
                    "subcategories": {
                        "scanners": {
                            "name": "Web Scanners",
                            "tools": [
                                {
                                    "name": "Burp Suite",
                                    "url": "https://portswigger.net/burp",
                                    "description": "Web security testing platform",
                                    "type": "freemium",
                                    "notation": "(F)†",
                                    "pricingNote": "Community: Free, Pro: $399/year",
                                    "isIndustryStandard": True,
                                    "tags": ["web", "proxy", "scanner"],
                                    "platforms": ["windows", "linux", "macos"],
                                    "links": [
                                        {
                                            "url": "https://portswigger.net/burp/documentation",
                                            "label": "Documentation",
                                            "type": "docs"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }
        
        for filename, content in self.test_files.items():
            with open(os.path.join(data_dir, filename), 'w') as f:
                json.dump(content, f, indent=2)
    
    def test_full_import_export_cycle(self):
        """Test complete import -> modify -> export cycle"""
        # Step 1: Import from JSON
        importer = JSONImporter()
        importer.import_all(self.test_dir)
        
        # Verify import
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM resources")
            self.assertEqual(cursor.fetchone()['count'], 4)  # Total tools
            
            cursor.execute("SELECT COUNT(*) as count FROM categories")
            self.assertGreater(cursor.fetchone()['count'], 4)  # Categories + subcategories
        
        # Step 2: Modify via API
        response = self.client.get('/api/resources?search=Nmap')
        data = json.loads(response.data)
        nmap_id = data['resources'][0]['id']
        
        update_data = {
            'name': 'Nmap - Updated',
            'description': 'Updated description via API',
            'url': 'https://nmap.org',
            'type': 'free',
            'is_community_favorite': True,
            'is_industry_standard': True,
            'tags': ['network', 'scanning', 'updated'],
            'platforms': ['windows', 'linux', 'macos', 'android'],
            'links': []
        }
        
        response = self.client.put(f'/api/resources/{nmap_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Export back to JSON
        export_dir = os.path.join(self.test_dir, 'export')
        exporter = JSONExporter()
        exporter.export_all(export_dir)
        
        # Step 4: Verify exported data
        exported_file = os.path.join(export_dir, 'src', 'data', 'tools', 'reconnaissance.json')
        with open(exported_file, 'r') as f:
            exported = json.load(f)
        
        # Find updated Nmap
        port_scanners = exported['reconnaissance']['subcategories']['port_scanners']['tools']
        nmap = next(t for t in port_scanners if 'Nmap' in t['name'])
        
        self.assertEqual(nmap['name'], 'Nmap - Updated')
        self.assertEqual(nmap['description'], 'Updated description via API')
        self.assertIn('updated', nmap['tags'])
        self.assertIn('android', nmap['platforms'])
    
    def test_sync_detection_workflow(self):
        """Test the sync detection and resolution workflow"""
        # Import initial data
        importer = JSONImporter()
        importer.import_all(self.test_dir)
        
        # Check initial sync status
        response = self.client.get('/api/sync-status')
        data = json.loads(response.data)
        # Should be out of sync initially (no export done)
        self.assertEqual(data['sync_status'], 'db_newer')
        
        # Export to sync
        response = self.client.post('/api/export')
        self.assertEqual(response.status_code, 200)
        
        # Check sync status again
        response = self.client.get('/api/sync-status')
        data = json.loads(response.data)
        self.assertEqual(data['sync_status'], 'in_sync')
        
        # Make a database change
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE resources 
                SET description = 'Changed in database'
                WHERE name = 'Nmap'
            """)
            conn.commit()
        
        # Should be out of sync again
        response = self.client.get('/api/sync-status')
        data = json.loads(response.data)
        self.assertEqual(data['sync_status'], 'db_newer')
        self.assertGreater(data['db_changes'], 0)
        
        # Simulate external JSON change
        time.sleep(1)  # Ensure file timestamp is newer
        json_path = os.path.join(self.test_dir, 'src', 'data', 'tools', 'reconnaissance.json')
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        
        # Modify and write back
        json_data['reconnaissance']['subcategories']['port_scanners']['tools'][0]['description'] = 'Changed externally'
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        # Check sync status
        response = self.client.get('/api/sync-status')
        data = json.loads(response.data)
        self.assertEqual(data['sync_status'], 'json_newer')
        self.assertTrue(data['json_changes'])
    
    def test_category_management_integration(self):
        """Test category assignment and management"""
        # Import data
        importer = JSONImporter()
        importer.import_all(self.test_dir)
        
        # Get categories
        response = self.client.get('/api/categories')
        categories = json.loads(response.data)
        self.assertGreater(len(categories), 0)
        
        # Get a resource
        response = self.client.get('/api/resources?search=Burp')
        data = json.loads(response.data)
        burp_id = data['resources'][0]['id']
        
        # Get full resource details
        response = self.client.get(f'/api/resources/{burp_id}')
        resource = json.loads(response.data)
        
        # Should have categories from import
        self.assertGreater(len(resource['categories']), 0)
        
        # Update categories
        recon_cat = next(c for c in categories if c['name'] == 'Reconnaissance')
        web_cat = next(c for c in categories if c['name'] == 'Web Security')
        
        update_data = {
            'category_ids': [recon_cat['id'], web_cat['id']],
            'primary_category_id': web_cat['id']
        }
        
        response = self.client.put(f'/api/resources/{burp_id}/categories',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        response = self.client.get(f'/api/resources/{burp_id}')
        resource = json.loads(response.data)
        
        self.assertEqual(len(resource['categories']), 2)
        primary_cat = next(c for c in resource['categories'] if c['is_primary'])
        self.assertEqual(primary_cat['name'], 'Web Security')
    
    def test_health_dashboard_integration(self):
        """Test resource health monitoring"""
        # Create some problematic data
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Resource without description
            cursor.execute("""
                INSERT INTO resources (id, name, slug, url)
                VALUES ('no-desc', 'No Description Tool', 'no-desc', 'https://example.com')
            """)
            
            # Resource without URL
            cursor.execute("""
                INSERT INTO resources (id, name, slug, description)
                VALUES ('no-url', 'No URL Tool', 'no-url', 'Has description but no URL')
            """)
            
            # Duplicate URLs
            cursor.execute("""
                INSERT INTO resources (id, name, slug, url)
                VALUES ('dup-1', 'Duplicate 1', 'dup-1', 'https://duplicate.com')
            """)
            cursor.execute("""
                INSERT INTO resources (id, name, slug, url)
                VALUES ('dup-2', 'Duplicate 2', 'dup-2', 'https://duplicate.com')
            """)
            
            conn.commit()
        
        # Check health dashboard
        response = self.client.get('/api/resources/health')
        health = json.loads(response.data)
        
        self.assertGreater(health['missing_description'], 0)
        self.assertGreater(health['missing_url'], 0)
        self.assertGreater(health['duplicate_urls'], 0)
        self.assertGreater(len(health['needs_attention']), 0)
        
        # Verify specific issues
        issues = [r['issue'] for r in health['needs_attention']]
        self.assertIn('Missing description', issues)
        self.assertIn('Missing URL', issues)
    
    def test_bulk_operations_integration(self):
        """Test bulk operations workflow"""
        # Import data
        importer = JSONImporter()
        importer.import_all(self.test_dir)
        
        # Get all resources
        response = self.client.get('/api/resources?per_page=100')
        data = json.loads(response.data)
        
        # In a real implementation, bulk operations would be tested here
        # Currently these are TODO in the frontend
        self.assertGreater(len(data['resources']), 0)
        
        # Verify bulk operation endpoints exist (when implemented)
        # response = self.client.post('/api/bulk/update-type', ...)
        # response = self.client.post('/api/bulk/add-category', ...)
        # response = self.client.post('/api/bulk/delete', ...)
    
    def test_audit_trail_integration(self):
        """Test audit logging throughout the system"""
        # Import data
        importer = JSONImporter()
        importer.import_all(self.test_dir)
        
        # Make various changes
        response = self.client.get('/api/resources')
        resource_id = json.loads(response.data)['resources'][0]['id']
        
        # Update resource
        self.client.put(f'/api/resources/{resource_id}',
                       data=json.dumps({'name': 'Audited Change', 'tags': [], 'platforms': [], 'links': []}),
                       content_type='application/json')
        
        # Export
        self.client.post('/api/export')
        
        # Check audit log
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT action, COUNT(*) as count
                FROM audit_log
                GROUP BY action
            """)
            
            actions = {row['action']: row['count'] for row in cursor.fetchall()}
            
            # Should have various audit entries
            self.assertIn('update', actions)
            self.assertIn('json_export', actions)
            self.assertGreater(actions['update'], 0)


if __name__ == '__main__':
    unittest.main()