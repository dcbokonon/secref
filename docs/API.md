# SecRef Admin API Documentation

## Overview

The SecRef Admin API provides secure endpoints for managing cybersecurity resources. All endpoints require authentication and include comprehensive security measures.

## Base URL

```
https://secref.org/admin/api
```

## Authentication

All API requests require authentication using session cookies obtained through the login endpoint.

### Login

```http
POST /admin/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=your-password&csrf_token=token
```

**Response:**
```json
{
  "status": "success",
  "redirect": "/admin/"
}
```

### Logout

```http
POST /admin/logout
```

## Security

- **CSRF Protection**: All state-changing requests require a valid CSRF token
- **Rate Limiting**: 100 requests per minute per IP
- **Input Validation**: All inputs are validated and sanitized
- **HTTPS Only**: API only accessible over HTTPS

## Endpoints

### Resources

#### List Resources

```http
GET /admin/api/resources
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 50, max: 100)
- `search` (string): Search query
- `category` (string): Filter by category
- `type` (string): Filter by type (free, paid, freemium, enterprise)

**Response:**
```json
{
  "resources": [
    {
      "id": "nmap",
      "name": "Nmap",
      "url": "https://nmap.org",
      "description": "Network discovery and security auditing",
      "category": "network-tools",
      "type": "free",
      "is_community_favorite": true,
      "is_industry_standard": true,
      "created_at": "2025-06-26T00:00:00Z",
      "updated_at": "2025-06-26T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 892,
    "pages": 18
  }
}
```

#### Get Resource

```http
GET /admin/api/resources/{id}
```

**Response:**
```json
{
  "id": "nmap",
  "name": "Nmap",
  "url": "https://nmap.org",
  "description": "Network discovery and security auditing",
  "category": "network-tools",
  "subcategory": "port-scanners",
  "type": "free",
  "notation": "",
  "pricing_note": null,
  "is_community_favorite": true,
  "is_industry_standard": true,
  "tags": ["network", "scanning", "discovery"],
  "platforms": ["windows", "linux", "macos"],
  "extra_data": {},
  "created_at": "2025-06-26T00:00:00Z",
  "updated_at": "2025-06-26T00:00:00Z"
}
```

#### Create Resource

```http
POST /admin/api/resources
Content-Type: application/json

{
  "name": "New Tool",
  "url": "https://example.com",
  "description": "Tool description",
  "category": "network-tools",
  "type": "freemium",
  "csrf_token": "token"
}
```

**Response:**
```json
{
  "status": "success",
  "resource": {
    "id": "new-tool",
    "name": "New Tool",
    "url": "https://example.com"
  }
}
```

#### Update Resource

```http
PUT /admin/api/resources/{id}
Content-Type: application/json

{
  "name": "Updated Tool Name",
  "description": "Updated description",
  "csrf_token": "token"
}
```

**Response:**
```json
{
  "status": "success",
  "resource": {
    "id": "tool-id",
    "name": "Updated Tool Name"
  }
}
```

#### Delete Resource

```http
DELETE /admin/api/resources/{id}

{
  "csrf_token": "token"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Resource deleted"
}
```

### Bulk Operations

#### Bulk Update

```http
POST /admin/api/resources/bulk-update
Content-Type: application/json

{
  "resource_ids": ["id1", "id2", "id3"],
  "updates": {
    "category": "new-category",
    "is_community_favorite": true
  },
  "csrf_token": "token"
}
```

**Response:**
```json
{
  "status": "success",
  "updated": 3,
  "failed": 0
}
```

#### Bulk Delete

```http
POST /admin/api/resources/bulk-delete
Content-Type: application/json

{
  "resource_ids": ["id1", "id2", "id3"],
  "csrf_token": "token"
}
```

**Response:**
```json
{
  "status": "success",
  "deleted": 3,
  "failed": 0
}
```

### Import/Export

#### Export Resources

```http
GET /admin/api/export?format=json
```

**Query Parameters:**
- `format` (string): Export format (json, csv)
- `category` (string): Filter by category

**Response:**
- JSON format: Resource array
- CSV format: CSV file download

#### Import Resources

```http
POST /admin/api/import
Content-Type: multipart/form-data

file=@resources.json
csrf_token=token
```

**Response:**
```json
{
  "status": "success",
  "imported": 45,
  "skipped": 2,
  "errors": []
}
```

### System

#### Health Check

```http
GET /admin/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "uptime": 86400
}
```

#### Statistics

```http
GET /admin/api/stats
```

**Response:**
```json
{
  "total_resources": 892,
  "by_category": {
    "network-tools": 156,
    "web-security": 203
  },
  "by_type": {
    "free": 543,
    "freemium": 201,
    "paid": 148
  },
  "community_favorites": 87,
  "industry_standards": 42,
  "last_updated": "2025-06-26T00:00:00Z"
}
```

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "name": "Name is required",
      "url": "Invalid URL format"
    }
  }
}
```

### Error Codes

- `AUTHENTICATION_REQUIRED`: User not authenticated
- `PERMISSION_DENIED`: User lacks required permissions
- `VALIDATION_ERROR`: Input validation failed
- `NOT_FOUND`: Resource not found
- `DUPLICATE_RESOURCE`: Resource already exists
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

## Rate Limiting

- **Default limit**: 100 requests per minute
- **Headers returned**:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

## Data Validation

### Resource Fields

- **name**: Required, 3-100 characters
- **url**: Required, valid URL format
- **description**: Required, 10-500 characters
- **category**: Required, must exist in category list
- **type**: Required, one of: free, freemium, paid, enterprise
- **tags**: Array of strings, max 10 tags
- **platforms**: Array of strings, valid platforms only

### Special Characters

All text inputs are sanitized to prevent XSS. Allowed HTML tags in descriptions:
- `<strong>`, `<em>`, `<code>`, `<a>` (with rel="nofollow")

## Examples

### cURL Examples

#### Login
```bash
curl -X POST https://secref.org/admin/login \
  -d "username=admin&password=password" \
  -c cookies.txt
```

#### Get Resources
```bash
curl https://secref.org/admin/api/resources \
  -b cookies.txt
```

#### Create Resource
```bash
curl -X POST https://secref.org/admin/api/resources \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "New Tool",
    "url": "https://example.com",
    "description": "A new security tool",
    "category": "network-tools",
    "type": "free",
    "csrf_token": "token"
  }'
```

### Python Example

```python
import requests

# Login
session = requests.Session()
login_data = {
    'username': 'admin',
    'password': 'password'
}
session.post('https://secref.org/admin/login', data=login_data)

# Get CSRF token
response = session.get('https://secref.org/admin/')
csrf_token = extract_csrf_token(response.text)

# Create resource
resource_data = {
    'name': 'New Tool',
    'url': 'https://example.com',
    'description': 'A new security tool',
    'category': 'network-tools',
    'type': 'free',
    'csrf_token': csrf_token
}
response = session.post(
    'https://secref.org/admin/api/resources',
    json=resource_data
)
print(response.json())
```

## Webhooks (Future)

Planned webhook support for:
- Resource created
- Resource updated
- Resource deleted
- Bulk operations completed

## API Versioning

The API uses URL versioning. Current version: v1 (implicit).

Future versions will be accessed at:
```
https://secref.org/admin/api/v2/resources
```

## Support

For API support or to report issues:
- GitHub Issues: https://github.com/dcbokonon/secref/issues
- Email: api@secref.org