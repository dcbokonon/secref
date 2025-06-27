"""
Input validation and sanitization for SecRef admin
"""

import re
import bleach
from urllib.parse import urlparse

# Allowed HTML tags for descriptions
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'code', 'pre', 'ul', 'ol', 'li']
ALLOWED_ATTRIBUTES = {}

# URL validation patterns
ALLOWED_SCHEMES = ['http', 'https', 'ftp', 'ftps', 'git']
JAVASCRIPT_PATTERN = re.compile(r'javascript:', re.IGNORECASE)

# Field length limits
MAX_LENGTHS = {
    'name': 200,
    'slug': 200,
    'description': 5000,
    'url': 500,
    'tag': 50,
    'platform': 50,
    'pricing_note': 500,
    'popularity_note': 500,
    'notation': 20
}

def sanitize_html(text):
    """Sanitize HTML content"""
    if not text:
        return text
    
    # Clean HTML
    cleaned = bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return cleaned

def validate_url(url):
    """Validate and sanitize URL"""
    if not url:
        return None
    
    # Strip whitespace
    url = url.strip()
    
    # Check for javascript: protocol
    if JAVASCRIPT_PATTERN.search(url):
        raise ValueError("JavaScript URLs are not allowed")
    
    # Parse URL
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme and parsed.scheme not in ALLOWED_SCHEMES:
            raise ValueError(f"URL scheme '{parsed.scheme}' is not allowed")
        
        # Ensure URL has scheme
        if not parsed.scheme:
            url = 'https://' + url
            parsed = urlparse(url)
        
        # Basic validation
        if not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        return url
    
    except Exception as e:
        raise ValueError(f"Invalid URL: {str(e)}")

def validate_length(field_name, value, max_length=None):
    """Validate field length"""
    if not value:
        return value
    
    # Get max length from defaults or parameter
    if max_length is None:
        max_length = MAX_LENGTHS.get(field_name, 1000)
    
    if len(value) > max_length:
        raise ValueError(f"{field_name} exceeds maximum length of {max_length} characters")
    
    return value

def validate_slug(slug):
    """Validate slug format"""
    if not slug:
        return slug
    
    # Check length
    slug = validate_length('slug', slug)
    
    # Check format (lowercase, alphanumeric, hyphens)
    if not re.match(r'^[a-z0-9-]+$', slug):
        raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
    
    return slug

def validate_resource_type(resource_type):
    """Validate resource type"""
    allowed_types = ['tool', 'technique', 'service', 'platform', 'framework', 'library', 'resource']
    
    if resource_type and resource_type not in allowed_types:
        raise ValueError(f"Invalid resource type. Allowed types: {', '.join(allowed_types)}")
    
    return resource_type

def validate_difficulty(difficulty):
    """Validate difficulty level"""
    allowed_levels = ['beginner', 'intermediate', 'advanced', 'expert']
    
    if difficulty and difficulty not in allowed_levels:
        raise ValueError(f"Invalid difficulty. Allowed levels: {', '.join(allowed_levels)}")
    
    return difficulty

def validate_resource_data(data):
    """Validate all resource data"""
    errors = {}
    
    # Required fields
    if not data.get('name'):
        errors['name'] = 'Name is required'
    else:
        try:
            data['name'] = validate_length('name', data['name'])
        except ValueError as e:
            errors['name'] = str(e)
    
    # URL validation
    if data.get('url'):
        try:
            data['url'] = validate_url(data['url'])
        except ValueError as e:
            errors['url'] = str(e)
    
    # Description sanitization
    if data.get('description'):
        try:
            data['description'] = validate_length('description', data['description'])
            data['description'] = sanitize_html(data['description'])
        except ValueError as e:
            errors['description'] = str(e)
    
    # Type validation
    if data.get('type') and data['type'] not in ['free', 'paid', 'freemium', 'enterprise']:
        errors['type'] = 'Invalid pricing type'
    
    # Resource type validation
    if data.get('resource_type'):
        try:
            data['resource_type'] = validate_resource_type(data['resource_type'])
        except ValueError as e:
            errors['resource_type'] = str(e)
    
    # Difficulty validation
    if data.get('difficulty'):
        try:
            data['difficulty'] = validate_difficulty(data['difficulty'])
        except ValueError as e:
            errors['difficulty'] = str(e)
    
    # Validate other fields
    for field in ['notation', 'pricing_note', 'popularity_note']:
        if data.get(field):
            try:
                data[field] = validate_length(field, data[field])
                data[field] = sanitize_html(data[field])
            except ValueError as e:
                errors[field] = str(e)
    
    # Validate tags
    if data.get('tags'):
        validated_tags = []
        for tag in data['tags']:
            try:
                tag = validate_length('tag', tag)
                # Simple alphanumeric + common chars validation
                if re.match(r'^[a-zA-Z0-9\s\-_]+$', tag):
                    validated_tags.append(tag.strip())
                else:
                    errors.setdefault('tags', []).append(f"Invalid tag: {tag}")
            except ValueError as e:
                errors.setdefault('tags', []).append(str(e))
        data['tags'] = validated_tags
    
    # Validate platforms
    if data.get('platforms'):
        validated_platforms = []
        for platform in data['platforms']:
            try:
                platform = validate_length('platform', platform)
                if re.match(r'^[a-zA-Z0-9\s\-_]+$', platform):
                    validated_platforms.append(platform.strip().lower())
                else:
                    errors.setdefault('platforms', []).append(f"Invalid platform: {platform}")
            except ValueError as e:
                errors.setdefault('platforms', []).append(str(e))
        data['platforms'] = validated_platforms
    
    # Validate links
    if data.get('links'):
        validated_links = []
        for i, link in enumerate(data['links']):
            if link.get('url'):
                try:
                    link['url'] = validate_url(link['url'])
                    if link.get('label'):
                        link['label'] = validate_length('label', link['label'], 100)
                        link['label'] = sanitize_html(link['label'])
                    validated_links.append(link)
                except ValueError as e:
                    errors.setdefault('links', []).append(f"Link {i+1}: {str(e)}")
        data['links'] = validated_links
    
    return data, errors