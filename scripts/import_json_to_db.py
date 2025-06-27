#!/usr/bin/env python3
"""Import all JSON data into PostgreSQL database"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid
from slugify import slugify

from db_config import get_db_connection, init_schema

class JSONImporter:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.category_map = {}  # Maps category paths to UUIDs
        self.resource_count = 0
        
    def import_all(self, base_path: str):
        """Import all JSON files from the data directory"""
        try:
            with get_db_connection() as self.conn:
                self.cursor = self.conn.cursor()
                
                # Clear existing data (optional)
                if input("Clear existing data? (y/N): ").lower() == 'y':
                    self.clear_data()
                
                # Import all JSON files
                data_path = Path(base_path) / "src" / "data"
                self.import_directory(data_path)
                
                print(f"\nImport complete! Total resources imported: {self.resource_count}")
                
        except Exception as e:
            print(f"Import failed: {e}")
            raise
    
    def clear_data(self):
        """Clear all existing data"""
        print("Clearing existing data...")
        self.cursor.execute("TRUNCATE resources, categories CASCADE")
        self.conn.commit()
    
    def import_directory(self, directory: Path, parent_category: str = ""):
        """Recursively import JSON files from directory"""
        for item in directory.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Create category for directory
                category_name = item.name.replace('-', ' ').title()
                category_path = f"{parent_category}/{item.name}" if parent_category else item.name
                
                # Recurse into subdirectory
                self.import_directory(item, category_path)
                
            elif item.suffix == '.json' and item.name not in ['schema.json', 'site-content.json']:
                print(f"\nImporting: {item}")
                self.import_json_file(item, parent_category)
    
    def import_json_file(self, file_path: Path, parent_category: str):
        """Import a single JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Extract metadata
        metadata = data.get('metadata', {})
        file_category = file_path.stem  # filename without extension
        
        # Create top-level category for this file
        category_path = f"{parent_category}/{file_category}" if parent_category else file_category
        category_id = self.ensure_category(
            slug=file_category,
            name=metadata.get('title', file_category.replace('-', ' ').title()),
            description=metadata.get('description', ''),
            parent_path=parent_category
        )
        
        # Process categories in the file
        if 'categories' in data:
            self.process_categories(data['categories'], category_id, category_path)
    
    def ensure_category(self, slug: str, name: str, description: str = "", 
                       parent_path: str = "") -> str:
        """Ensure category exists and return its ID"""
        # Check if we already created this category
        full_path = f"{parent_path}/{slug}" if parent_path else slug
        if full_path in self.category_map:
            return self.category_map[full_path]
        
        # Get parent ID if there's a parent path
        parent_id = None
        if parent_path and parent_path in self.category_map:
            parent_id = self.category_map[parent_path]
        
        # Check if category exists
        self.cursor.execute("""
            SELECT id FROM categories 
            WHERE slug = %s AND (parent_id = %s OR (parent_id IS NULL AND %s IS NULL))
        """, (slug, parent_id, parent_id))
        
        result = self.cursor.fetchone()
        if result:
            category_id = result['id']
        else:
            # Create new category
            category_id = str(uuid.uuid4())
            self.cursor.execute("""
                INSERT INTO categories (id, parent_id, slug, name, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (category_id, parent_id, slug, name, description))
        
        self.category_map[full_path] = category_id
        return category_id
    
    def process_categories(self, categories: List[Dict], parent_id: str, parent_path: str):
        """Process categories array"""
        for idx, category in enumerate(categories):
            # Create category
            cat_slug = category.get('id', slugify(category.get('title', f'category-{idx}')))
            cat_id = self.ensure_category(
                slug=cat_slug,
                name=category.get('title', ''),
                description=category.get('description', ''),
                parent_path=parent_path
            )
            
            cat_path = f"{parent_path}/{cat_slug}"
            
            # Process subcategories
            if 'subcategories' in category:
                self.process_subcategories(category['subcategories'], cat_id, cat_path)
            
            # Process items
            if 'items' in category:
                self.process_items(category['items'], cat_id)
    
    def process_subcategories(self, subcategories: List[Dict], parent_id: str, parent_path: str):
        """Process subcategories recursively"""
        for idx, subcat in enumerate(subcategories):
            # Create subcategory
            subcat_slug = subcat.get('id', slugify(subcat.get('title', f'subcat-{idx}')))
            subcat_id = self.ensure_category(
                slug=subcat_slug,
                name=subcat.get('title', ''),
                description=subcat.get('description', ''),
                parent_path=parent_path
            )
            
            subcat_path = f"{parent_path}/{subcat_slug}"
            
            # Process nested subcategories
            if 'subcategories' in subcat:
                self.process_subcategories(subcat['subcategories'], subcat_id, subcat_path)
            
            # Process items
            if 'items' in subcat:
                self.process_items(subcat['items'], subcat_id)
    
    def process_items(self, items: List[Dict], category_id: str):
        """Process items array"""
        for item in items:
            self.import_resource(item, category_id)
    
    def import_resource(self, item: Dict[str, Any], category_id: str):
        """Import a single resource"""
        # Generate UUID and slug
        resource_id = str(uuid.uuid4())
        slug = slugify(item['name'])
        
        # Prepare base fields
        base_fields = {
            'id': resource_id,
            'name': item['name'],
            'slug': slug,
            'description': item.get('description'),
            'url': item.get('url'),
            'type': item.get('type'),
            'resource_type': item.get('resourceType'),
            'difficulty': item.get('difficulty'),
            'status': item.get('status'),
            'notation': item.get('notation'),
            'pricing_note': item.get('pricingNote'),
            'is_community_favorite': item.get('isCommunityFavorite', False),
            'is_industry_standard': item.get('isIndustryStandard', False),
            'popularity_note': item.get('popularityNote'),
            'location': item.get('location'),
            'locations': json.dumps(item['locations']) if 'locations' in item and isinstance(item['locations'], list) else item.get('locations'),
            'schedule': item.get('schedule'),
            'cost': item.get('cost'),
            'duration': item.get('duration'),
            'features': json.dumps(item['features']) if 'features' in item else None,
            'domains': json.dumps(item['domains']) if 'domains' in item else None
        }
        
        # Collect any extra fields
        known_fields = set(base_fields.keys()) | {'name', 'tags', 'platforms', 'links', 'authors', 
                                                  'games', 'alternatives', 'practiceExams', 'studyResources'}
        extra_data = {k: v for k, v in item.items() if k not in known_fields}
        if extra_data:
            base_fields['extra_data'] = json.dumps(extra_data)
        
        # Insert resource
        columns = [k for k, v in base_fields.items() if v is not None]
        values = [v for k, v in base_fields.items() if v is not None]
        
        query = f"""
            INSERT INTO resources ({', '.join(columns)})
            VALUES ({', '.join(['%s'] * len(values))})
            ON CONFLICT (slug) DO UPDATE SET
                {', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col not in ['id', 'slug']])}
            RETURNING id
        """
        
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        resource_id = result['id']
        
        # Link to category
        self.cursor.execute("""
            INSERT INTO resource_categories (resource_id, category_id, is_primary)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (resource_id, category_id, True))
        
        # Add tags
        if 'tags' in item and item['tags']:
            for tag in item['tags']:
                self.cursor.execute("""
                    INSERT INTO resource_tags (resource_id, tag)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (resource_id, tag))
        
        # Add platforms
        if 'platforms' in item and item['platforms']:
            for platform in item['platforms']:
                self.cursor.execute("""
                    INSERT INTO resource_platforms (resource_id, platform)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (resource_id, platform))
        
        # Add links
        if 'links' in item and isinstance(item['links'], list):
            for idx, link in enumerate(item['links']):
                self.cursor.execute("""
                    INSERT INTO resource_links (resource_id, url, label, type, sort_order)
                    VALUES (%s, %s, %s, %s, %s)
                """, (resource_id, link['url'], link['label'], link.get('type'), idx))
        
        self.resource_count += 1
        if self.resource_count % 100 == 0:
            print(f"  Imported {self.resource_count} resources...")
            self.conn.commit()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--init':
        print("Initializing database schema...")
        init_schema()
    
    base_path = '/Users/mike/code/cyber/secref'
    importer = JSONImporter()
    importer.import_all(base_path)

if __name__ == '__main__':
    main()