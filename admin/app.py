#!/usr/bin/env python3
"""Secure admin interface for SecRef database"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, abort
from flask_login import LoginManager, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

# Import after path setup
from config import get_config
from models import User
from auth import auth_bp
from validators import validate_resource_data, validate_url, sanitize_html
from db_config_sqlite import get_db_connection
from export_sqlite_to_json import JSONExporter
import json
import uuid

# Initialize Flask app
app = Flask(__name__)
config = get_config()
app.config.from_object(config)

# Security extensions
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=config.RATELIMIT_STORAGE_URL,
    default_limits=[config.RATELIMIT_DEFAULT]
)

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler(
    config.LOG_FILE,
    maxBytes=config.LOG_MAX_BYTES,
    backupCount=config.LOG_BACKUP_COUNT
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
app.logger.addHandler(file_handler)
app.logger.setLevel(getattr(logging, config.LOG_LEVEL))
app.logger.info('SecRef admin startup')

# Register blueprints
app.register_blueprint(auth_bp)

# Login manager
@login_manager.user_loader
def load_user(username):
    return User.get(username)

# Security headers
@app.after_request
def set_security_headers(response):
    """Set security headers on all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-downgrade'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    
    if not config.DEBUG:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response

# Error handlers
@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify({'error': 'Forbidden'}), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f'Internal error: {str(e)}')
    return jsonify({'error': 'Internal server error'}), 500

# Routes
@app.route('/')
@login_required
def index():
    """Main admin page"""
    return render_template('index.html', username=current_user.username)

@app.route('/api/check-duplicate', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def check_duplicate():
    """Check if a URL already exists"""
    url = request.json.get('url', '').strip()
    resource_id = request.json.get('resource_id')
    
    if not url:
        return jsonify({'duplicate': False})
    
    try:
        # Validate URL
        url = validate_url(url)
    except ValueError:
        return jsonify({'error': 'Invalid URL'}), 400
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Use parameterized query
        if resource_id:
            cursor.execute(
                "SELECT id, name, slug FROM resources WHERE url = ? AND id != ?",
                (url, resource_id)
            )
        else:
            cursor.execute(
                "SELECT id, name, slug FROM resources WHERE url = ?",
                (url,)
            )
        
        duplicate = cursor.fetchone()
        
        if duplicate:
            return jsonify({
                'duplicate': True,
                'resource': dict(duplicate)
            })
        
        return jsonify({'duplicate': False})

@app.route('/api/resources')
@login_required
def get_resources():
    """Get all resources with pagination and search"""
    search = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 100)  # Max 100 per page
    offset = (page - 1) * per_page
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Build query with parameterized search
        if search:
            # Sanitize search term
            search_term = f'%{search}%'
            
            # Get total count
            cursor.execute(
                "SELECT COUNT(*) as count FROM resources WHERE name LIKE ? OR description LIKE ?",
                (search_term, search_term)
            )
            total = cursor.fetchone()['count']
            
            # Get resources
            cursor.execute("""
                SELECT r.*, 
                       GROUP_CONCAT(DISTINCT t.tag) as tags,
                       GROUP_CONCAT(DISTINCT p.platform) as platforms
                FROM resources r
                LEFT JOIN resource_tags t ON r.id = t.resource_id
                LEFT JOIN resource_platforms p ON r.id = p.resource_id
                WHERE r.name LIKE ? OR r.description LIKE ?
                GROUP BY r.id
                ORDER BY r.name
                LIMIT ? OFFSET ?
            """, (search_term, search_term, per_page, offset))
        else:
            # Get total count
            cursor.execute("SELECT COUNT(*) as count FROM resources")
            total = cursor.fetchone()['count']
            
            # Get resources
            cursor.execute("""
                SELECT r.*, 
                       GROUP_CONCAT(DISTINCT t.tag) as tags,
                       GROUP_CONCAT(DISTINCT p.platform) as platforms
                FROM resources r
                LEFT JOIN resource_tags t ON r.id = t.resource_id
                LEFT JOIN resource_platforms p ON r.id = p.resource_id
                GROUP BY r.id
                ORDER BY r.name
                LIMIT ? OFFSET ?
            """, (per_page, offset))
        
        resources = cursor.fetchall()
        
        # Convert to list of dicts
        result = []
        for r in resources:
            resource = dict(r)
            resource['tags'] = r['tags'].split(',') if r['tags'] else []
            resource['platforms'] = r['platforms'].split(',') if r['platforms'] else []
            resource['is_community_favorite'] = bool(resource['is_community_favorite'])
            resource['is_industry_standard'] = bool(resource['is_industry_standard'])
            result.append(resource)
        
        return jsonify({
            'resources': result,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        })

@app.route('/api/resources/health')
@login_required
def get_resource_health():
    """Get resource health statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        metrics = {}
        
        # Total resources
        cursor.execute("SELECT COUNT(*) as count FROM resources")
        metrics['total'] = cursor.fetchone()['count']
        
        # Missing descriptions
        cursor.execute(
            "SELECT COUNT(*) as count FROM resources WHERE description IS NULL OR description = ''"
        )
        metrics['missing_description'] = cursor.fetchone()['count']
        
        # Missing URLs
        cursor.execute(
            "SELECT COUNT(*) as count FROM resources WHERE url IS NULL OR url = ''"
        )
        metrics['missing_url'] = cursor.fetchone()['count']
        
        # Resources without categories
        cursor.execute("""
            SELECT COUNT(DISTINCT r.id) as count 
            FROM resources r
            LEFT JOIN resource_categories rc ON r.id = rc.resource_id
            WHERE rc.resource_id IS NULL
        """)
        metrics['no_categories'] = cursor.fetchone()['count']
        
        # Duplicate URLs
        cursor.execute("""
            SELECT url, COUNT(*) as count 
            FROM resources 
            WHERE url IS NOT NULL AND url != ''
            GROUP BY url 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        metrics['duplicate_urls'] = len(duplicates)
        metrics['duplicate_url_list'] = [dict(d) for d in duplicates[:10]]
        
        # Type distribution
        cursor.execute("""
            SELECT type, COUNT(*) as count 
            FROM resources 
            GROUP BY type 
            ORDER BY count DESC
        """)
        metrics['type_distribution'] = [dict(r) for r in cursor.fetchall()]
        
        # Recently updated
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM resources 
            WHERE updated_at > datetime('now', '-7 days')
        """)
        metrics['recently_updated'] = cursor.fetchone()['count']
        
        # Resources needing attention
        cursor.execute("""
            SELECT id, name, 
                   CASE 
                     WHEN description IS NULL OR description = '' THEN 'Missing description'
                     WHEN url IS NULL OR url = '' THEN 'Missing URL'
                     WHEN resource_type IS NULL THEN 'Missing resource type'
                   END as issue
            FROM resources
            WHERE (description IS NULL OR description = '') 
               OR (url IS NULL OR url = '')
               OR resource_type IS NULL
            LIMIT 20
        """)
        metrics['needs_attention'] = [dict(r) for r in cursor.fetchall()]
        
        return jsonify(metrics)

@app.route('/api/resources/<resource_id>')
@login_required
def get_resource(resource_id):
    """Get a single resource with all details"""
    # Validate UUID format
    try:
        uuid.UUID(resource_id)
    except ValueError:
        return jsonify({'error': 'Invalid resource ID'}), 400
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get resource
        cursor.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
        resource = cursor.fetchone()
        
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        
        resource = dict(resource)
        
        # Get tags
        cursor.execute("SELECT tag FROM resource_tags WHERE resource_id = ?", (resource_id,))
        resource['tags'] = [r['tag'] for r in cursor.fetchall()]
        
        # Get platforms
        cursor.execute("SELECT platform FROM resource_platforms WHERE resource_id = ?", (resource_id,))
        resource['platforms'] = [r['platform'] for r in cursor.fetchall()]
        
        # Get links
        cursor.execute("SELECT * FROM resource_links WHERE resource_id = ? ORDER BY sort_order", (resource_id,))
        resource['links'] = [dict(r) for r in cursor.fetchall()]
        
        # Get categories
        cursor.execute("""
            SELECT c.*, rc.is_primary FROM categories c
            JOIN resource_categories rc ON c.id = rc.category_id
            WHERE rc.resource_id = ?
        """, (resource_id,))
        categories = []
        for row in cursor.fetchall():
            cat = dict(row)
            cat['is_primary'] = bool(cat['is_primary'])
            categories.append(cat)
        resource['categories'] = categories
        
        # Convert booleans
        resource['is_community_favorite'] = bool(resource['is_community_favorite'])
        resource['is_industry_standard'] = bool(resource['is_industry_standard'])
        
        return jsonify(resource)

@app.route('/api/resources/<resource_id>', methods=['PUT'])
@login_required
@limiter.limit("30 per minute")
def update_resource(resource_id):
    """Update a resource"""
    # Validate UUID format
    try:
        uuid.UUID(resource_id)
    except ValueError:
        return jsonify({'error': 'Invalid resource ID'}), 400
    
    data = request.json
    
    # Validate and sanitize input
    data, errors = validate_resource_data(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check resource exists
        cursor.execute("SELECT id FROM resources WHERE id = ?", (resource_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Resource not found'}), 404
        
        # Update main resource
        cursor.execute("""
            UPDATE resources SET
                name = ?, description = ?, url = ?, type = ?, resource_type = ?,
                difficulty = ?, notation = ?, pricing_note = ?,
                is_community_favorite = ?, is_industry_standard = ?, popularity_note = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            data['name'], data.get('description'), data.get('url'),
            data.get('type'), data.get('resource_type'), data.get('difficulty'),
            data.get('notation'), data.get('pricing_note'),
            1 if data.get('is_community_favorite') else 0,
            1 if data.get('is_industry_standard') else 0,
            data.get('popularity_note'),
            resource_id
        ))
        
        # Update tags
        cursor.execute("DELETE FROM resource_tags WHERE resource_id = ?", (resource_id,))
        for tag in data.get('tags', []):
            cursor.execute("INSERT INTO resource_tags (resource_id, tag) VALUES (?, ?)", 
                         (resource_id, tag))
        
        # Update platforms
        cursor.execute("DELETE FROM resource_platforms WHERE resource_id = ?", (resource_id,))
        for platform in data.get('platforms', []):
            cursor.execute("INSERT INTO resource_platforms (resource_id, platform) VALUES (?, ?)", 
                         (resource_id, platform))
        
        # Update links
        cursor.execute("DELETE FROM resource_links WHERE resource_id = ?", (resource_id,))
        for idx, link in enumerate(data.get('links', [])):
            cursor.execute("""
                INSERT INTO resource_links (id, resource_id, url, label, type, sort_order)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), resource_id, link['url'], link.get('label'), 
                  link.get('type'), idx))
        
        # Add audit log entry
        cursor.execute("""
            INSERT INTO audit_log (table_name, record_id, action, new_data, changed_by)
            VALUES ('resources', ?, 'update', ?, ?)
        """, (resource_id, json.dumps(data), current_user.username))
        
        conn.commit()
        
        app.logger.info(f'Resource {resource_id} updated by {current_user.username}')
        
    return jsonify({'success': True})

@app.route('/api/import', methods=['POST'])
@login_required
@limiter.limit("5 per hour")
def import_from_json():
    """Import JSON files to database"""
    try:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Import using the existing import script
        from import_json_to_sqlite import JSONImporter
        importer = JSONImporter()
        
        # Clear and reimport all data
        importer.import_all(base_path, clear_existing=True)
        
        # Record import time
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (table_name, record_id, action, changed_by)
                VALUES ('system', 'import', 'json_import', ?)
            """, (current_user.username,))
            conn.commit()
        
        app.logger.info(f'JSON import completed by {current_user.username}')
        
        return jsonify({'success': True, 'message': 'Import completed successfully'})
    except Exception as e:
        app.logger.error(f'Import failed: {str(e)}')
        return jsonify({'success': False, 'error': 'Import failed'}), 500

@app.route('/api/export', methods=['POST'])
@login_required
@limiter.limit("10 per hour")
def export_to_json():
    """Export database to JSON files"""
    try:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        exporter = JSONExporter()
        exporter.export_all(base_path)
        
        # Record export time
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (table_name, record_id, action, changed_by)
                VALUES ('system', 'export', 'json_export', ?)
            """, (current_user.username,))
            conn.commit()
        
        app.logger.info(f'JSON export completed by {current_user.username}')
        
        return jsonify({'success': True, 'message': 'Export completed successfully'})
    except Exception as e:
        app.logger.error(f'Export failed: {str(e)}')
        return jsonify({'success': False, 'error': 'Export failed'}), 500

@app.route('/api/sync-status')
@login_required
def get_sync_status():
    """Check if database is in sync with JSON files"""
    import glob
    from datetime import datetime
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get last export time
        cursor.execute("""
            SELECT changed_at FROM audit_log 
            WHERE action = 'json_export' 
            ORDER BY changed_at DESC 
            LIMIT 1
        """)
        last_export = cursor.fetchone()
        
        # Get last import time
        cursor.execute("""
            SELECT changed_at FROM audit_log 
            WHERE action = 'json_import' 
            ORDER BY changed_at DESC 
            LIMIT 1
        """)
        last_import = cursor.fetchone()
        
        # Get last resource update time
        cursor.execute("SELECT MAX(updated_at) as last_update FROM resources")
        last_update = cursor.fetchone()
        
        # Check JSON file modification times
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_files = glob.glob(os.path.join(base_path, 'src', 'data', '**', '*.json'), recursive=True)
        newest_json_time = None
        if json_files:
            newest_json_time = max(os.path.getmtime(f) for f in json_files)
            newest_json_time = datetime.fromtimestamp(newest_json_time).strftime('%Y-%m-%d %H:%M:%S')
        
        # Determine sync direction needed
        sync_status = 'in_sync'
        db_changes = 0
        json_changes = False
        
        # Check for database changes not exported
        if last_export:
            cursor.execute("""
                SELECT COUNT(*) as count FROM audit_log 
                WHERE action = 'update' 
                AND changed_at > ?
            """, (last_export['changed_at'],))
            db_changes = cursor.fetchone()['count']
        else:
            cursor.execute("SELECT COUNT(*) as count FROM resources")
            db_changes = cursor.fetchone()['count']
        
        # Check for JSON changes not imported
        if newest_json_time:
            last_sync_time = max(filter(None, [
                last_export['changed_at'] if last_export else None,
                last_import['changed_at'] if last_import else None,
                '2000-01-01 00:00:00'
            ]))
            json_changes = newest_json_time > last_sync_time
        
        if db_changes > 0:
            sync_status = 'db_newer'
        elif json_changes:
            sync_status = 'json_newer'
        
        return jsonify({
            'last_export': last_export['changed_at'] if last_export else None,
            'last_import': last_import['changed_at'] if last_import else None,
            'last_update': last_update['last_update'] if last_update else None,
            'newest_json': newest_json_time,
            'db_changes': db_changes,
            'json_changes': json_changes,
            'sync_status': sync_status,
            'in_sync': sync_status == 'in_sync'
        })

@app.route('/api/categories')
@login_required
def get_categories():
    """Get category tree"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get all categories
        cursor.execute("""
            SELECT * FROM categories 
            ORDER BY parent_id, sort_order, name
        """)
        
        categories = cursor.fetchall()
        
        # Build tree
        tree = []
        by_id = {}
        
        for cat in categories:
            cat = dict(cat)
            by_id[cat['id']] = cat
            cat['children'] = []
        
        for cat in by_id.values():
            if cat['parent_id']:
                if cat['parent_id'] in by_id:
                    by_id[cat['parent_id']]['children'].append(cat)
            else:
                tree.append(cat)
        
        return jsonify(tree)

@app.route('/api/resources/<resource_id>/categories', methods=['PUT'])
@login_required
@limiter.limit("30 per minute")
def update_resource_categories(resource_id):
    """Update the categories for a resource"""
    # Validate UUID format
    try:
        uuid.UUID(resource_id)
    except ValueError:
        return jsonify({'error': 'Invalid resource ID'}), 400
    
    data = request.json
    category_ids = data.get('category_ids', [])
    primary_category_id = data.get('primary_category_id', None)
    
    # Validate category IDs
    for cat_id in category_ids:
        try:
            uuid.UUID(cat_id)
        except ValueError:
            return jsonify({'error': f'Invalid category ID: {cat_id}'}), 400
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check resource exists
        cursor.execute("SELECT id FROM resources WHERE id = ?", (resource_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Resource not found'}), 404
        
        # First, remove all existing category associations
        cursor.execute("DELETE FROM resource_categories WHERE resource_id = ?", (resource_id,))
        
        # Then add the new associations
        for idx, category_id in enumerate(category_ids):
            is_primary = (category_id == primary_category_id) if primary_category_id else (idx == 0)
            cursor.execute("""
                INSERT INTO resource_categories (resource_id, category_id, is_primary, sort_order)
                VALUES (?, ?, ?, ?)
            """, (resource_id, category_id, 1 if is_primary else 0, idx))
        
        # Add audit log entry
        cursor.execute("""
            INSERT INTO audit_log (table_name, record_id, action, new_data, changed_by)
            VALUES ('resources', ?, 'update', ?, ?)
        """, (resource_id, json.dumps(data), current_user.username))
        
        conn.commit()
        
        app.logger.info(f'Categories updated for resource {resource_id} by {current_user.username}')
        
    return jsonify({'success': True})

if __name__ == '__main__':
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Check for admin credentials
    if not config.ADMIN_PASSWORD_HASH and not config.DEVELOPMENT_MODE:
        print("ERROR: No admin password hash configured.")
        print("Generate one with:")
        print("python -c \"from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))\"")
        print("Then set ADMIN_PASSWORD_HASH in your .env file")
        sys.exit(1)
    
    print(f"Admin interface running at http://localhost:{config.FLASK_PORT or 5001}")
    print("Use Ctrl+C to stop")
    
    # Run app
    app.run(
        debug=config.DEBUG,
        port=int(os.environ.get('FLASK_PORT', 5001)),
        host='127.0.0.1'
    )