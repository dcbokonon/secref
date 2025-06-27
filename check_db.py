#!/usr/bin/env python3
"""Quick database status check"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

from db_config_sqlite import get_db_connection

def check_database():
    """Check database status and show statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Count resources
            cursor.execute("SELECT COUNT(*) as count FROM resources")
            resource_count = cursor.fetchone()['count']
            
            # Count by type
            cursor.execute("""
                SELECT type, COUNT(*) as count 
                FROM resources 
                WHERE type IS NOT NULL 
                GROUP BY type 
                ORDER BY count DESC
            """)
            type_counts = cursor.fetchall()
            
            # Count community favorites and industry standards
            cursor.execute("""
                SELECT 
                    SUM(is_community_favorite) as favorites,
                    SUM(is_industry_standard) as standards
                FROM resources
            """)
            badges = cursor.fetchone()
            
            # Count categories
            cursor.execute("SELECT COUNT(*) as count FROM categories")
            category_count = cursor.fetchone()['count']
            
            print("=== SecRef Database Status ===")
            print(f"\nTotal Resources: {resource_count}")
            print(f"Total Categories: {category_count}")
            print(f"\nCommunity Favorites (⭐): {badges['favorites'] or 0}")
            print(f"Industry Standards (🏆): {badges['standards'] or 0}")
            print(f"\nResources by Type:")
            for t in type_counts:
                print(f"  {t['type']}: {t['count']}")
            
            print(f"\nDatabase location: {os.path.abspath('database/secref.db')}")
            print("\nTo start the admin interface, run: ./start_admin.sh")
            
    except Exception as e:
        print(f"Error checking database: {e}")
        print("Make sure you've run the import script first:")
        print("  python3 scripts/import_json_to_sqlite.py")

if __name__ == '__main__':
    check_database()