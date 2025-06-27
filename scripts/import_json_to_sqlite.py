#!/usr/bin/env python3
"""Import all JSON data into SQLite database"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid
from slugify import slugify

from db_config_sqlite import get_db_connection, init_schema

class JSONImporter:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.category_map = {}  # Maps category paths to UUIDs
        self.resource_count = 0
        
    def import_all(self, base_path: str, clear_existing=False):
        """Import all JSON files from the data directory"""
        try:
            with get_db_connection() as self.conn:
                self.cursor = self.conn.cursor()
                
                # Clear existing data if requested
                if clear_existing:
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
        tables = ['resource_platforms', 'resource_tags', 'resource_links', 
                 'resource_categories', 'resources', 'categories']
        for table in tables:
            self.cursor.execute(f"DELETE FROM {table}")
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
        if parent_id:
            self.cursor.execute("""
                SELECT id FROM categories 
                WHERE slug = ? AND parent_id = ?
            """, (slug, parent_id))
        else:
            self.cursor.execute("""
                SELECT id FROM categories 
                WHERE slug = ? AND parent_id IS NULL
            """, (slug,))
        
        result = self.cursor.fetchone()
        if result:
            category_id = result['id']
        else:
            # Create new category
            category_id = str(uuid.uuid4())
            self.cursor.execute("""
                INSERT INTO categories (id, parent_id, slug, name, description)
                VALUES (?, ?, ?, ?, ?)
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
        
        # Convert lists to JSON strings for SQLite
        locations_json = json.dumps(item['locations']) if 'locations' in item and isinstance(item['locations'], list) else item.get('locations')
        features_json = json.dumps(item['features']) if 'features' in item else None
        domains_json = json.dumps(item['domains']) if 'domains' in item else None
        
        # Collect any extra fields
        known_fields = {'name', 'description', 'url', 'type', 'resourceType', 'difficulty',
                       'status', 'notation', 'pricingNote', 'isCommunityFavorite', 'isIndustryStandard',
                       'popularityNote', 'location', 'locations', 'schedule', 'cost', 'duration',
                       'features', 'domains', 'tags', 'platforms', 'links', 'authors', 
                       'games', 'alternatives', 'practiceExams', 'studyResources'}
        extra_data = {k: v for k, v in item.items() if k not in known_fields}
        extra_data_json = json.dumps(extra_data) if extra_data else None
        
        # Check if resource exists
        self.cursor.execute("SELECT id FROM resources WHERE slug = ?", (slug,))
        existing = self.cursor.fetchone()
        
        if existing:
            resource_id = existing['id']
            # Update existing resource
            self.cursor.execute("""
                UPDATE resources SET
                    name = ?, description = ?, url = ?, type = ?, resource_type = ?,
                    difficulty = ?, status = ?, notation = ?, pricing_note = ?,
                    is_community_favorite = ?, is_industry_standard = ?, popularity_note = ?,
                    location = ?, locations = ?, schedule = ?, cost = ?, duration = ?,
                    features = ?, domains = ?, extra_data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                item['name'], item.get('description'), item.get('url'), item.get('type'),
                item.get('resourceType'), item.get('difficulty'), item.get('status'),
                item.get('notation'), item.get('pricingNote'),
                1 if item.get('isCommunityFavorite') else 0,
                1 if item.get('isIndustryStandard') else 0,
                item.get('popularityNote'), item.get('location'), locations_json,
                item.get('schedule'), item.get('cost'), item.get('duration'),
                features_json, domains_json, extra_data_json, resource_id
            ))
        else:
            # Insert new resource
            self.cursor.execute("""
                INSERT INTO resources (
                    id, name, slug, description, url, type, resource_type,
                    difficulty, status, notation, pricing_note,
                    is_community_favorite, is_industry_standard, popularity_note,
                    location, locations, schedule, cost, duration,
                    features, domains, extra_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resource_id, item['name'], slug, item.get('description'), item.get('url'),
                item.get('type'), item.get('resourceType'), item.get('difficulty'),
                item.get('status'), item.get('notation'), item.get('pricingNote'),
                1 if item.get('isCommunityFavorite') else 0,
                1 if item.get('isIndustryStandard') else 0,
                item.get('popularityNote'), item.get('location'), locations_json,
                item.get('schedule'), item.get('cost'), item.get('duration'),
                features_json, domains_json, extra_data_json
            ))
        
        # Link to category
        self.cursor.execute("""
            INSERT OR IGNORE INTO resource_categories (resource_id, category_id, is_primary)
            VALUES (?, ?, ?)
        """, (resource_id, category_id, 1))
        
        # Clear existing tags, platforms, links for this resource
        self.cursor.execute("DELETE FROM resource_tags WHERE resource_id = ?", (resource_id,))
        self.cursor.execute("DELETE FROM resource_platforms WHERE resource_id = ?", (resource_id,))
        self.cursor.execute("DELETE FROM resource_links WHERE resource_id = ?", (resource_id,))
        
        # Add tags
        if 'tags' in item and item['tags']:
            for tag in item['tags']:
                self.cursor.execute("""
                    INSERT INTO resource_tags (resource_id, tag)
                    VALUES (?, ?)
                """, (resource_id, tag))
        
        # Add platforms
        if 'platforms' in item and item['platforms']:
            for platform in item['platforms']:
                self.cursor.execute("""
                    INSERT INTO resource_platforms (resource_id, platform)
                    VALUES (?, ?)
                """, (resource_id, platform))
        
        # Add links
        if 'links' in item and isinstance(item['links'], list):
            for idx, link in enumerate(item['links']):
                link_id = str(uuid.uuid4())
                self.cursor.execute("""
                    INSERT INTO resource_links (id, resource_id, url, label, type, sort_order)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (link_id, resource_id, link['url'], link['label'], link.get('type'), idx))
        
        self.resource_count += 1
        if self.resource_count % 100 == 0:
            print(f"  Imported {self.resource_count} resources...")
            self.conn.commit()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--init':
        print("Initializing database schema...")
        init_schema()
        return
    
    clear_existing = len(sys.argv) > 1 and sys.argv[1] == '--clear'
    
    base_path = '/Users/mike/code/cyber/secref'
    importer = JSONImporter()
    importer.import_all(base_path, clear_existing=clear_existing)

if __name__ == '__main__':
    main()