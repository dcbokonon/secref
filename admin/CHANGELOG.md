# SecRef Admin Changelog

## Improved Category Management UI

### Changes Made:

1. **Enhanced Category Tree Display**
   - Added search/filter functionality to quickly find categories
   - Shows full category paths (e.g., "Reconnaissance > Network Discovery > Port Scanners")
   - Better visual hierarchy with improved indentation and styling
   - Collapsible/expandable tree nodes with smooth animations

2. **Better Category Selection**
   - Selected categories now show as cards with full path information
   - Primary category clearly marked with green background
   - Click star (★) to change primary category
   - Visual feedback when hovering over categories

3. **Improved Organization**
   - Security tool categories prioritized at the top
   - Auto-expands to show selected categories when editing
   - Maintains selection state properly when switching between resources

4. **Search Functionality**
   - Real-time filtering of categories as you type
   - Shows count of matching categories
   - Auto-expands tree to reveal matching items

### How to Use:

1. When editing a resource, scroll down to the Categories section
2. Use the search box to quickly find relevant categories
3. Check/uncheck boxes to add/remove categories
4. Selected categories appear below with full paths
5. Click the star on any selected category to make it primary
6. Save changes to update the resource

### Technical Details:

- Categories are loaded from the SQLite database via `/api/categories`
- Resources can belong to multiple categories with one marked as primary
- The tree structure supports unlimited nesting levels
- All changes are persisted to the database when saved