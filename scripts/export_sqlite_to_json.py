#!/usr/bin/env python3
"""Export SQLite database back to JSON files"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

from db_config_sqlite import get_db_connection

class JSONExporter:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def export_all(self, base_path: str):
        """Export all data from database to JSON files"""
        try:
            with get_db_connection() as self.conn:
                self.cursor = self.conn.cursor()
                
                # Get top-level categories (no parent)
                self.cursor.execute("""
                    SELECT id, slug, name, description 
                    FROM categories 
                    WHERE parent_id IS NULL
                    ORDER BY sort_order, name
                """)
                
                top_categories = self.cursor.fetchall()
                
                for category in top_categories:
                    self.export_category(category, base_path)
                
                print("\nExport complete!")
                
        except Exception as e:
            print(f"Export failed: {e}")
            raise
    
    def export_category(self, category: Dict, base_path: str):
        """Export a single category and its contents"""
        slug = category['slug']
        
        # Determine output path based on category type
        if slug in ['tools', 'learning', 'communities', 'career', 'practice', 
                    'specialized-domains', 'references', 'news']:
            # These are directory categories
            output_dir = Path(base_path) / "src" / "data" / slug
            
            # Get child categories (files)
            self.cursor.execute("""
                SELECT id, slug, name, description 
                FROM categories 
                WHERE parent_id = ?
                ORDER BY sort_order, name
            """, (category['id'],))
            
            child_categories = self.cursor.fetchall()
            
            for child in child_categories:
                self.export_file_category(child, output_dir)
        else:
            # This is a file category
            output_dir = Path(base_path) / "src" / "data"
            self.export_file_category(category, output_dir)
    
    def export_file_category(self, category: Dict, output_dir: Path):
        """Export a category that represents a JSON file"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Build the JSON structure
        data = {
            "metadata": {
                "title": category['name'],
                "description": category['description'] or "",
                "lastUpdated": "2025-06-25",
                "totalItems": self.count_items_recursive(category['id'])
            }
        }
        
        # Get categories and build structure
        categories_data = self.build_categories_structure(category['id'])
        if categories_data:
            data['categories'] = categories_data
        
        # Get direct items
        items = self.get_items_for_category(category['id'])
        if items:
            data['items'] = items
        
        # Write JSON file
        output_file = output_dir / f"{category['slug']}.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported: {output_file}")
    
    def build_categories_structure(self, parent_id: str) -> List[Dict]:
        """Build hierarchical category structure"""
        # Get child categories
        self.cursor.execute("""
            SELECT id, slug, name, description 
            FROM categories 
            WHERE parent_id = ?
            ORDER BY sort_order, name
        """, (parent_id,))
        
        categories = self.cursor.fetchall()
        result = []
        
        for cat in categories:
            cat_data = {
                "id": cat['slug'],
                "title": cat['name'],
                "description": cat['description'] or ""
            }
            
            # Get subcategories
            subcats = self.build_subcategories_structure(cat['id'])
            if subcats:
                cat_data['subcategories'] = subcats
            
            # Get items
            items = self.get_items_for_category(cat['id'])
            if items:
                cat_data['items'] = items
            
            result.append(cat_data)
        
        return result
    
    def build_subcategories_structure(self, parent_id: str) -> List[Dict]:
        """Build subcategories structure recursively"""
        # Get child categories
        self.cursor.execute("""
            SELECT id, slug, name, description 
            FROM categories 
            WHERE parent_id = ?
            ORDER BY sort_order, name
        """, (parent_id,))
        
        subcategories = self.cursor.fetchall()
        result = []
        
        for subcat in subcategories:
            subcat_data = {
                "id": subcat['slug'],
                "title": subcat['name'],
                "description": subcat['description'] or ""
            }
            
            # Get nested subcategories
            nested = self.build_subcategories_structure(subcat['id'])
            if nested:
                subcat_data['subcategories'] = nested
            
            # Get items
            items = self.get_items_for_category(subcat['id'])
            if items:
                subcat_data['items'] = items
            
            result.append(subcat_data)
        
        return result
    
    def get_items_for_category(self, category_id: str) -> List[Dict]:
        """Get all items for a category"""
        # Query resources with all related data
        self.cursor.execute("""
            SELECT r.*, rc.is_primary
            FROM resources r
            JOIN resource_categories rc ON r.id = rc.resource_id
            WHERE rc.category_id = ?
            ORDER BY rc.sort_order, r.name
        """, (category_id,))
        
        resources = self.cursor.fetchall()
        items = []
        
        for resource in resources:
            item = {
                "name": resource['name']
            }
            
            # Add fields only if they have values
            if resource['description']:
                item['description'] = resource['description']
            if resource['url']:
                item['url'] = resource['url']
            if resource['type']:
                item['type'] = resource['type']
            if resource['resource_type']:
                item['resourceType'] = resource['resource_type']
            if resource['difficulty']:
                item['difficulty'] = resource['difficulty']
            if resource['status']:
                item['status'] = resource['status']
            if resource['notation']:
                item['notation'] = resource['notation']
            if resource['pricing_note']:
                item['pricingNote'] = resource['pricing_note']
            if resource['is_community_favorite']:
                item['isCommunityFavorite'] = True
            if resource['is_industry_standard']:
                item['isIndustryStandard'] = True
            if resource['popularity_note']:
                item['popularityNote'] = resource['popularity_note']
            if resource['location']:
                item['location'] = resource['location']
            if resource['locations']:
                try:
                    item['locations'] = json.loads(resource['locations'])
                except:
                    item['locations'] = resource['locations']
            if resource['schedule']:
                item['schedule'] = resource['schedule']
            if resource['cost']:
                item['cost'] = resource['cost']
            if resource['duration']:
                item['duration'] = resource['duration']
            if resource['features']:
                try:
                    item['features'] = json.loads(resource['features'])
                except:
                    pass
            if resource['domains']:
                try:
                    item['domains'] = json.loads(resource['domains'])
                except:
                    pass
            
            # Get platforms
            self.cursor.execute("""
                SELECT platform FROM resource_platforms
                WHERE resource_id = ?
                ORDER BY platform
            """, (resource['id'],))
            platforms = [row['platform'] for row in self.cursor.fetchall()]
            if platforms:
                item['platforms'] = platforms
            
            # Get tags
            self.cursor.execute("""
                SELECT tag FROM resource_tags
                WHERE resource_id = ?
                ORDER BY tag
            """, (resource['id'],))
            tags = [row['tag'] for row in self.cursor.fetchall()]
            if tags:
                item['tags'] = tags
            
            # Get links
            self.cursor.execute("""
                SELECT url, label, type FROM resource_links
                WHERE resource_id = ?
                ORDER BY sort_order
            """, (resource['id'],))
            links = self.cursor.fetchall()
            if links:
                item['links'] = [
                    {k: v for k, v in link.items() if v is not None}
                    for link in links
                ]
            
            # Add extra data if any
            if resource['extra_data']:
                try:
                    extra = json.loads(resource['extra_data'])
                    item.update(extra)
                except:
                    pass
            
            items.append(item)
        
        return items
    
    def count_items_recursive(self, category_id: str) -> int:
        """Count all items under a category recursively"""
        # Count direct items
        self.cursor.execute("""
            SELECT COUNT(*) as count FROM resource_categories
            WHERE category_id = ?
        """, (category_id,))
        count = self.cursor.fetchone()['count']
        
        # Count items in subcategories
        self.cursor.execute("""
            SELECT id FROM categories WHERE parent_id = ?
        """, (category_id,))
        
        for subcat in self.cursor.fetchall():
            count += self.count_items_recursive(subcat['id'])
        
        return count

def main():
    base_path = '/Users/mike/code/cyber/secref'
    exporter = JSONExporter()
    exporter.export_all(base_path)

if __name__ == '__main__':
    main()