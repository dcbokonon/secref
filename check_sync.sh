#!/bin/bash
# Check if database and JSON files are in sync before committing

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if database exists
if [ ! -f "database/secref.db" ]; then
    echo -e "${GREEN}✓ No database found - using JSON files only${NC}"
    exit 0
fi

# Check sync status using the API (if admin is running)
if curl -s http://localhost:5001/api/sync-status > /dev/null 2>&1; then
    # Admin is running, use API
    RESPONSE=$(curl -s http://localhost:5001/api/sync-status)
    SYNC_STATUS=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['sync_status'])")
    
    if [ "$SYNC_STATUS" = "in_sync" ]; then
        echo -e "${GREEN}✓ Database and JSON files are in sync${NC}"
        exit 0
    elif [ "$SYNC_STATUS" = "db_newer" ]; then
        DB_CHANGES=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['db_changes'])")
        echo -e "${YELLOW}⚠️  Warning: Database has $DB_CHANGES changes not in JSON files${NC}"
        echo -e "${YELLOW}   Run the admin interface and click 'Export to JSON' before committing${NC}"
        exit 1
    elif [ "$SYNC_STATUS" = "json_newer" ]; then
        echo -e "${YELLOW}⚠️  Warning: JSON files have external changes not in database${NC}"
        echo -e "${YELLOW}   Run the admin interface and click 'Import from JSON' to sync${NC}"
        echo -e "${YELLOW}   This can happen after pulling changes from git${NC}"
        exit 1
    fi
else
    # Admin not running, do basic check
    echo -e "${YELLOW}ℹ️  Admin interface not running - cannot verify sync status${NC}"
    echo -e "${YELLOW}   Start admin with: python3 admin/app.py${NC}"
    
    # Check if JSON files exist and are recent
    if [ -f "src/data/tools/reconnaissance.json" ]; then
        JSON_TIME=$(stat -f %m src/data/tools/reconnaissance.json 2>/dev/null || stat -c %Y src/data/tools/reconnaissance.json)
        DB_TIME=$(stat -f %m database/secref.db 2>/dev/null || stat -c %Y database/secref.db)
        
        if [ "$DB_TIME" -gt "$JSON_TIME" ]; then
            echo -e "${RED}⚠️  Database is newer than JSON files - you may have uncommitted changes${NC}"
            exit 1
        fi
    fi
fi