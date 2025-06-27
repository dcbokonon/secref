#!/bin/bash
# Start the SecRef admin interface

echo "Starting SecRef Admin Interface..."
echo "The admin will be available at http://localhost:5001"
echo ""
echo "To stop the admin later, press Ctrl+C or run: pkill -f 'python3.*app.py'"
echo ""

# Start Flask
python3 admin/app.py