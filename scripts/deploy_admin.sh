#!/bin/bash
# Deploy admin panel to production server

set -e  # Exit on error

echo "SecRef Admin Panel Deployment Script"
echo "===================================="

# Configuration
SERVER="149.28.63.158"
USER="root"  # Change if you use a different user
DEPLOY_DIR="/var/www/secref"
ADMIN_DIR="$DEPLOY_DIR/admin"

# Check if we can connect to server
echo "Testing server connection..."
ssh -o ConnectTimeout=5 $USER@$SERVER "echo 'Connection successful'" || {
    echo "ERROR: Cannot connect to server. Please check SSH access."
    exit 1
}

echo ""
echo "This script will:"
echo "1. Copy admin panel files to the server"
echo "2. Set up Python virtual environment"
echo "3. Install dependencies"
echo "4. Create systemd service for admin panel"
echo "5. Configure environment variables"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Create admin directory on server
echo "Creating admin directory..."
ssh $USER@$SERVER "mkdir -p $ADMIN_DIR"

# Copy admin files
echo "Copying admin files..."
rsync -avz --exclude='__pycache__' --exclude='*.pyc' \
    admin/ $USER@$SERVER:$ADMIN_DIR/

# Copy scripts needed for database
echo "Copying database scripts..."
ssh $USER@$SERVER "mkdir -p $DEPLOY_DIR/scripts"
rsync -avz scripts/*.py $USER@$SERVER:$DEPLOY_DIR/scripts/

# Copy database directory structure
echo "Creating database directory..."
ssh $USER@$SERVER "mkdir -p $DEPLOY_DIR/database"

# Set up Python environment on server
echo "Setting up Python environment..."
ssh $USER@$SERVER << 'EOF'
cd /var/www/secref/admin
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

# Create .env file
echo "Setting up environment variables..."
echo ""
echo "You need to provide:"
echo "1. A secret key for Flask sessions"
echo "2. An admin password"
echo ""

# Generate secret key
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
echo "Generated SECRET_KEY: $SECRET_KEY"

# Get admin password
read -sp "Enter admin password: " ADMIN_PASSWORD
echo ""

# Generate password hash
ADMIN_HASH=$(python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('$ADMIN_PASSWORD'))")

# Create .env file on server
ssh $USER@$SERVER << EOF
cd $ADMIN_DIR
cat > .env << 'ENV_FILE'
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$SECRET_KEY
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=$ADMIN_HASH
DATABASE_PATH=$DEPLOY_DIR/database/secref.db
ENV_FILE
chmod 600 .env
EOF

# Initialize database
echo "Initializing database..."
ssh $USER@$SERVER << EOF
cd $DEPLOY_DIR
source admin/venv/bin/activate
export PYTHONPATH=$DEPLOY_DIR
python scripts/db_config_sqlite.py
python scripts/import_json_to_sqlite.py
chown -R www-data:www-data database/
EOF

# Create systemd service
echo "Creating systemd service..."
ssh $USER@$SERVER << 'EOF'
cat > /etc/systemd/system/secref-admin.service << 'SERVICE'
[Unit]
Description=SecRef Admin Panel
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/secref/admin
Environment="PATH=/var/www/secref/admin/venv/bin"
Environment="PYTHONPATH=/var/www/secref"
ExecStart=/var/www/secref/admin/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable secref-admin
systemctl start secref-admin
EOF

# Check if service is running
echo "Checking service status..."
ssh $USER@$SERVER "systemctl status secref-admin --no-pager"

# Update Caddy to serve the site
echo "Updating Caddy configuration..."
ssh $USER@$SERVER << 'EOF'
# Copy the Caddyfile if it exists locally
systemctl reload caddy
EOF

echo ""
echo "Deployment complete!"
echo "Admin panel should be accessible at: https://secref.org/admin"
echo ""
echo "To check logs:"
echo "  ssh $USER@$SERVER 'journalctl -u secref-admin -f'"
echo ""
echo "To restart service:"
echo "  ssh $USER@$SERVER 'systemctl restart secref-admin'"