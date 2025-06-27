# SecRef Admin Interface

A web-based admin interface for managing the SecRef database.

## Features

- **Search & Browse**: Search through all 1169 resources with real-time filtering
- **Edit Resources**: Full editing capabilities for all resource fields
- **Tag Management**: Add/remove tags and platforms with a clean UI
- **Link Management**: Manage multiple links per resource with labels and types
- **Community Indicators**: Mark resources as community favorites or industry standards
- **Export to JSON**: One-click export to regenerate all JSON files from database

## Starting the Admin

```bash
# From the project root directory
python3 admin/app.py
```

The admin will be available at http://localhost:5001

## Using the Admin

### Searching Resources
- Use the search box to filter resources by name or description
- Browse through pages of results (50 per page)

### Editing Resources
1. Click "Edit" next to any resource
2. Update fields in the modal form:
   - Basic info (name, description, URL)
   - Resource type and difficulty
   - Pricing notation (e.g., "(F)†" for freemium with registration)
   - Community indicators (⭐ favorite, 🏆 industry standard)
   - Tags and platforms (press Enter to add)
   - Multiple links with labels and types

3. Click "Save Changes" to update the database

### Exporting to JSON
- Click the green "Export to JSON" button
- This regenerates all JSON files in `src/data/` from the database
- Use this after making edits to update the static site

## Database Location

The SQLite database is stored at:
```
database/secref.db
```

## Architecture

- **Flask** web framework for the admin interface
- **SQLite** database for zero-dependency storage
- **Two-way sync** between database and JSON files
- **Clean UI** with inline editing and modal forms