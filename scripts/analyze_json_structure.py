#!/usr/bin/env python3
"""Analyze all JSON files to understand the data structure"""

import json
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, Any

def analyze_json_files(base_path: str) -> Dict[str, Any]:
    """Analyze all JSON files in the data directory"""
    
    all_fields = defaultdict(set)
    all_resource_types = set()
    all_difficulties = set()
    all_types = set()
    all_link_types = set()
    max_depth = 0
    total_items = 0
    
    data_path = Path(base_path) / "src" / "data"
    
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                print(f"Analyzing: {file_path}")
                
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Analyze structure
                analyze_structure(data, all_fields, all_resource_types, 
                                all_difficulties, all_types, all_link_types)
                
                # Count items
                total_items += count_items(data)
    
    return {
        'fields': {k: list(v) for k, v in all_fields.items()},
        'resource_types': list(all_resource_types),
        'difficulties': list(all_difficulties),
        'types': list(all_types),
        'link_types': list(all_link_types),
        'total_items': total_items
    }

def analyze_structure(data: Any, all_fields: Dict, all_resource_types: Set,
                     all_difficulties: Set, all_types: Set, all_link_types: Set,
                     level: int = 0):
    """Recursively analyze data structure"""
    
    if isinstance(data, dict):
        # Skip metadata
        if 'categories' in data:
            for category in data.get('categories', []):
                analyze_structure(category, all_fields, all_resource_types,
                                all_difficulties, all_types, all_link_types, level + 1)
        
        if 'subcategories' in data:
            for sub in data['subcategories']:
                analyze_structure(sub, all_fields, all_resource_types,
                                all_difficulties, all_types, all_link_types, level + 1)
        
        if 'items' in data:
            for item in data['items']:
                # Record all fields
                for field, value in item.items():
                    all_fields[field].add(type(value).__name__)
                
                # Track enum values
                if 'resourceType' in item:
                    all_resource_types.add(item['resourceType'])
                if 'difficulty' in item:
                    all_difficulties.add(item['difficulty'])
                if 'type' in item:
                    all_types.add(item['type'])
                
                # Track link types
                if 'links' in item and isinstance(item['links'], list):
                    for link in item['links']:
                        if 'type' in link:
                            all_link_types.add(link['type'])

def count_items(data: Any) -> int:
    """Count total items in structure"""
    count = 0
    
    if isinstance(data, dict):
        if 'items' in data:
            count += len(data['items'])
        
        for category in data.get('categories', []):
            count += count_items(category)
        
        for sub in data.get('subcategories', []):
            count += count_items(sub)
    
    return count

if __name__ == '__main__':
    base_path = '/Users/mike/code/cyber/secref'
    results = analyze_json_files(base_path)
    
    print("\n=== Analysis Results ===")
    print(f"\nTotal items: {results['total_items']}")
    
    print("\nAll fields found:")
    for field, types in sorted(results['fields'].items()):
        print(f"  {field}: {', '.join(types)}")
    
    print(f"\nResource types: {results['resource_types']}")
    print(f"Difficulties: {results['difficulties']}")
    print(f"Types (free/paid): {results['types']}")
    print(f"Link types: {results['link_types']}")