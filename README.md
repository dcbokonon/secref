# SecRef

A clean, no-BS directory of cybersecurity resources. 

Visit: https://secref.org

## What is this?

Instead of bookmarking 500 different security sites, just bookmark this one. It's a simple directory that organizes tools, learning resources, communities, and everything else security-related.

No ads. No tracking. No user accounts. Just links.

## Architecture

SecRef uses a dual architecture approach:
- **Public Site**: Static Astro site serving JSON data files
- **Admin Panel**: Secure Flask application for resource management
- **Database**: SQLite for admin operations, exports to JSON for the static site

## Setup

### Prerequisites
- Node.js v20+ (use `nvm use` if you have nvm)
- Python 3.9+
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/dcbokonon/secref.git
   cd secref
   ```

2. **Set up the Astro site**
   ```bash
   npm install
   npm run dev  # Runs on http://localhost:4321
   ```

3. **Set up the admin panel** (optional, only needed for content management)
   ```bash
   # Create Python virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r admin/requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env and set:
   # - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_hex(32))")
   # - ADMIN_PASSWORD_HASH (generate with: python scripts/generate_password_hash.py)
   
   # Initialize database
   python scripts/db_config_sqlite.py
   python scripts/import_json_to_sqlite.py
   
   # Run admin panel
   cd admin && flask run  # Runs on http://localhost:5001
   ```

### Docker Setup

For production deployment:
```bash
docker-compose up -d
```

## Development Workflow

### Adding Resources

**Option 1: Direct JSON edits** (for contributors)
1. Edit the appropriate JSON file in `src/data/`
2. Submit a pull request

**Option 2: Admin panel** (for maintainers)
1. Access the admin panel at `/admin`
2. Add/edit resources through the UI
3. Export to JSON when done

### Running Tests

```bash
# Python tests
python -m pytest

# JavaScript/TypeScript linting
npm run lint
```

## Project Structure

```
secref/
├── src/                # Astro static site
│   ├── data/          # JSON resource files
│   ├── pages/         # Astro pages
│   └── components/    # React components
├── admin/             # Flask admin panel
├── scripts/           # Database sync scripts
├── tests/             # Test suites
└── database/          # SQLite database (gitignored)
```

## Contributing

Found a broken link? Know a tool we missed? PRs welcome!

### Guidelines
- One resource per PR for easier review
- Include description and proper categorization
- Verify URLs are working
- Follow existing JSON structure

### Resource Format
```json
{
  "name": "Tool Name",
  "url": "https://example.com",
  "description": "Brief description",
  "type": "free|freemium|paid|enterprise",
  "tags": ["tag1", "tag2"],
  "isCommunityFavorite": false,
  "isIndustryStandard": false
}
```

## Security

- Admin panel requires authentication
- All inputs are sanitized
- CSRF protection enabled
- Rate limiting in place
- See [SECURITY.md](SECURITY.md) for reporting vulnerabilities

## License

MIT
