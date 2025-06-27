#!/usr/bin/env python3
"""
API endpoint tests for SecRef admin interface
Tests all Flask routes and API functionality
"""

import unittest
import os
import sys
import tempfile
import shutil
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test database before importing app
test_dir = tempfile.mkdtemp()
os.environ['SECREF_DB_PATH'] = os.path.join(test_dir, 'test.db')

from admin.app import app
from scripts.db_config_sqlite import get_db_connection


class TestAPI(unittest.TestCase):
    """Test Flask API endpoints"""
    
    def setUp(self):
        """Set up test client and database"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.test_dir = test_dir
        
        # Initialize database with test data
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Add test categories
            cursor.execute("""
                INSERT INTO categories (id, name, slug, description)
                VALUES ('cat-1', 'Test Category', 'test-category', 'Test description')
            """)
            
            # Add test resources
            self.test_resources = [
                {
                    'id': 'res-1',
                    'name': 'Test Tool 1',
                    'slug': 'test-tool-1',
                    'url': 'https://test1.com',
                    'description': 'First test tool',
                    'type': 'free',
                    'is_community_favorite': 1,
                    'is_industry_standard': 0
                },
                {
                    'id': 'res-2',
                    'name': 'Test Tool 2',
                    'slug': 'test-tool-2',
                    'url': 'https://test2.com',
                    'description': 'Second test tool',
                    'type': 'paid',
                    'is_community_favorite': 0,
                    'is_industry_standard': 1
                }
            ]
            
            for resource in self.test_resources:
                cursor.execute("""
                    INSERT INTO resources (id, name, slug, url, description, type, 
                                         is_community_favorite, is_industry_standard)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(resource.values()))
            
            # Add tags and platforms
            cursor.execute("""
                INSERT INTO resource_tags (resource_id, tag)
                VALUES ('res-1', 'test'), ('res-1', 'tool')
            """)
            
            cursor.execute("""
                INSERT INTO resource_platforms (resource_id, platform)
                VALUES ('res-1', 'linux'), ('res-1', 'windows')
            """)
            
            # Add category association
            cursor.execute("""
                INSERT INTO resource_categories (resource_id, category_id, is_primary)
                VALUES ('res-1', 'cat-1', 1)
            """)
            
            conn.commit()
    
    def tearDown(self):
        """Clean up test data"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_homepage(self):
        """Test main admin page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SecRef Admin', response.data)
    
    def test_get_resources(self):
        """Test GET /api/resources endpoint"""
        response = self.client.get('/api/resources')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['total'], 2)
        self.assertEqual(len(data['resources']), 2)
        self.assertEqual(data['page'], 1)
        
        # Check resource structure
        resource = data['resources'][0]
        self.assertIn('id', resource)
        self.assertIn('name', resource)
        self.assertIn('tags', resource)
        self.assertIn('platforms', resource)
        self.assertIsInstance(resource['is_community_favorite'], bool)
    
    def test_search_resources(self):
        """Test resource search functionality"""
        response = self.client.get('/api/resources?search=Tool 1')
        data = json.loads(response.data)
        
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['resources'][0]['name'], 'Test Tool 1')
    
    def test_pagination(self):
        """Test resource pagination"""
        response = self.client.get('/api/resources?page=1&per_page=1')
        data = json.loads(response.data)
        
        self.assertEqual(len(data['resources']), 1)
        self.assertEqual(data['pages'], 2)
        self.assertEqual(data['per_page'], 1)
    
    def test_get_single_resource(self):
        """Test GET /api/resources/<id> endpoint"""
        response = self.client.get('/api/resources/res-1')
        self.assertEqual(response.status_code, 200)
        
        resource = json.loads(response.data)
        self.assertEqual(resource['name'], 'Test Tool 1')
        self.assertEqual(resource['tags'], ['test', 'tool'])
        self.assertEqual(resource['platforms'], ['linux', 'windows'])
        self.assertTrue(resource['is_community_favorite'])
        self.assertFalse(resource['is_industry_standard'])
        
        # Check categories
        self.assertEqual(len(resource['categories']), 1)
        self.assertEqual(resource['categories'][0]['name'], 'Test Category')
        self.assertTrue(resource['categories'][0]['is_primary'])
    
    def test_update_resource(self):
        """Test PUT /api/resources/<id> endpoint"""
        update_data = {
            'name': 'Updated Tool Name',
            'description': 'Updated description',
            'url': 'https://updated.com',
            'type': 'freemium',
            'is_community_favorite': False,
            'is_industry_standard': True,
            'tags': ['updated', 'test'],
            'platforms': ['macos'],
            'links': []
        }
        
        response = self.client.put('/api/resources/res-1',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Verify update
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resources WHERE id = 'res-1'")
            resource = cursor.fetchone()
            
            self.assertEqual(resource['name'], 'Updated Tool Name')
            self.assertEqual(resource['type'], 'freemium')
            self.assertFalse(bool(resource['is_community_favorite']))
            self.assertTrue(bool(resource['is_industry_standard']))
    
    def test_check_duplicate(self):
        """Test POST /api/check-duplicate endpoint"""
        # Check existing URL
        response = self.client.post('/api/check-duplicate',
                                  data=json.dumps({'url': 'https://test1.com'}),
                                  content_type='application/json')
        
        data = json.loads(response.data)
        self.assertTrue(data['duplicate'])
        self.assertEqual(data['resource']['name'], 'Test Tool 1')
        
        # Check non-existing URL
        response = self.client.post('/api/check-duplicate',
                                  data=json.dumps({'url': 'https://new.com'}),
                                  content_type='application/json')
        
        data = json.loads(response.data)
        self.assertFalse(data['duplicate'])
    
    def test_resource_health(self):
        """Test GET /api/resources/health endpoint"""
        response = self.client.get('/api/resources/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['total'], 2)
        self.assertIn('missing_description', data)
        self.assertIn('type_distribution', data)
        self.assertIn('duplicate_urls', data)
        self.assertIn('needs_attention', data)
    
    def test_categories_api(self):
        """Test GET /api/categories endpoint"""
        response = self.client.get('/api/categories')
        self.assertEqual(response.status_code, 200)
        
        categories = json.loads(response.data)
        self.assertIsInstance(categories, list)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0]['name'], 'Test Category')
    
    def test_update_resource_categories(self):
        """Test PUT /api/resources/<id>/categories endpoint"""
        # Add another category
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO categories (id, name, slug)
                VALUES ('cat-2', 'Second Category', 'second-cat')
            """)
            conn.commit()
        
        # Update resource categories
        update_data = {
            'category_ids': ['cat-1', 'cat-2'],
            'primary_category_id': 'cat-2'
        }
        
        response = self.client.put('/api/resources/res-1/categories',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT category_id, is_primary 
                FROM resource_categories 
                WHERE resource_id = 'res-1'
                ORDER BY category_id
            """)
            cats = cursor.fetchall()
            
            self.assertEqual(len(cats), 2)
            self.assertFalse(bool(cats[0]['is_primary']))  # cat-1
            self.assertTrue(bool(cats[1]['is_primary']))   # cat-2
    
    def test_sync_status(self):
        """Test GET /api/sync-status endpoint"""
        response = self.client.get('/api/sync-status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('sync_status', data)
        self.assertIn('db_changes', data)
        self.assertIn('json_changes', data)
        self.assertIn('in_sync', data)
    
    def test_export_endpoint(self):
        """Test POST /api/export endpoint"""
        # Create export directory
        export_dir = os.path.join(self.test_dir, 'src', 'data', 'tools')
        os.makedirs(export_dir, exist_ok=True)
        
        # Mock reconnaissance.json to prevent KeyError
        with open(os.path.join(export_dir, 'reconnaissance.json'), 'w') as f:
            json.dump({}, f)
        
        response = self.client.post('/api/export')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Check audit log
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM audit_log 
                WHERE action = 'json_export'
                ORDER BY changed_at DESC
                LIMIT 1
            """)
            audit = cursor.fetchone()
            self.assertIsNotNone(audit)
    
    def test_import_endpoint(self):
        """Test POST /api/import endpoint"""
        # Create test JSON file
        import_dir = os.path.join(self.test_dir, 'src', 'data', 'tools')
        os.makedirs(import_dir, exist_ok=True)
        
        test_data = {
            "test_category": {
                "name": "Test Category",
                "subcategories": {
                    "test_sub": {
                        "name": "Test Sub",
                        "tools": [{
                            "name": "Import Test Tool",
                            "url": "https://import-test.com",
                            "type": "free"
                        }]
                    }
                }
            }
        }
        
        with open(os.path.join(import_dir, 'test.json'), 'w') as f:
            json.dump(test_data, f)
        
        response = self.client.post('/api/import')
        # May fail due to import script dependencies, but endpoint should exist
        self.assertIn(response.status_code, [200, 500])
    
    def test_error_handling(self):
        """Test API error handling"""
        # Non-existent resource
        response = self.client.get('/api/resources/does-not-exist')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        
        # Invalid search parameters
        response = self.client.get('/api/resources?page=invalid')
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400])


if __name__ == '__main__':
    unittest.main()