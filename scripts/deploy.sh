#!/bin/bash
# SecRef Deployment Script
# Automates deployment steps with safety checks

set -euo pipefail

# Configuration
DEPLOY_USER="secref"
DEPLOY_DIR="/opt/secref"
BACKUP_DIR="/var/backups/secref"
SERVICE_NAME="secref-admin"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root"
   exit 1
fi

# Parse arguments
ENVIRONMENT="${1:-production}"
SKIP_BACKUP="${2:-false}"

print_info "Deploying SecRef in $ENVIRONMENT mode"

# Pre-deployment checks
print_info "Running pre-deployment checks..."

# Check if service exists
if systemctl list-units --full -all | grep -Fq "$SERVICE_NAME.service"; then
    print_success "Service $SERVICE_NAME found"
else
    print_error "Service $SERVICE_NAME not found. Run initial setup first."
    exit 1
fi

# Check disk space
AVAILABLE_SPACE=$(df -BG "$DEPLOY_DIR" | awk 'NR==2 {print $4}' | sed 's/G//')
if [[ $AVAILABLE_SPACE -lt 2 ]]; then
    print_error "Insufficient disk space. At least 2GB required."
    exit 1
fi
print_success "Disk space check passed"

# Backup current deployment
if [[ "$SKIP_BACKUP" != "true" ]]; then
    print_info "Creating backup..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR/deploy"
    
    # Backup database
    sudo -u "$DEPLOY_USER" python3 "$DEPLOY_DIR/scripts/backup_database.py" \
        --backup-dir "$BACKUP_DIR" || {
        print_error "Database backup failed"
        exit 1
    }
    
    # Backup configuration
    cp "$DEPLOY_DIR/.env" "$BACKUP_DIR/deploy/.env.$(date +%Y%m%d_%H%M%S)"
    
    print_success "Backup completed"
else
    print_info "Skipping backup (--skip-backup specified)"
fi

# Stop services
print_info "Stopping services..."
systemctl stop "$SERVICE_NAME" || true
systemctl stop caddy || true
print_success "Services stopped"

# Pull latest code
print_info "Updating code..."
cd "$DEPLOY_DIR"

# Save local changes
if [[ -n $(git status -s) ]]; then
    print_info "Stashing local changes..."
    sudo -u "$DEPLOY_USER" git stash
fi

# Pull latest
sudo -u "$DEPLOY_USER" git pull origin main || {
    print_error "Git pull failed"
    exit 1
}
print_success "Code updated"

# Update dependencies
print_info "Updating dependencies..."

# Python dependencies
sudo -u "$DEPLOY_USER" bash -c "
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r admin/requirements.txt
" || {
    print_error "Python dependency update failed"
    exit 1
}

# Node dependencies
sudo -u "$DEPLOY_USER" npm ci || {
    print_error "Node dependency update failed"
    exit 1
}

print_success "Dependencies updated"

# Build frontend
print_info "Building frontend..."
sudo -u "$DEPLOY_USER" npm run build || {
    print_error "Frontend build failed"
    exit 1
}
print_success "Frontend built"

# Run database migrations
print_info "Running database migrations..."
if [[ -f "$DEPLOY_DIR/scripts/migrate.py" ]]; then
    sudo -u "$DEPLOY_USER" bash -c "
        source venv/bin/activate
        python scripts/migrate.py
    " || {
        print_error "Database migration failed"
        exit 1
    }
    print_success "Database migrated"
else
    print_info "No migrations to run"
fi

# Update permissions
print_info "Setting permissions..."
chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_DIR"
chmod 600 "$DEPLOY_DIR/.env"
chmod 755 "$DEPLOY_DIR/scripts"/*.sh
chmod 755 "$DEPLOY_DIR/scripts"/*.py
print_success "Permissions set"

# Reload systemd
systemctl daemon-reload

# Start services
print_info "Starting services..."
systemctl start "$SERVICE_NAME" || {
    print_error "Failed to start $SERVICE_NAME"
    journalctl -u "$SERVICE_NAME" -n 50
    exit 1
}

systemctl start caddy || {
    print_error "Failed to start Caddy"
    journalctl -u caddy -n 50
    exit 1
}

print_success "Services started"

# Health check
print_info "Running health check..."
sleep 5

# Check local health endpoint
if curl -sf http://localhost:5001/admin/api/health > /dev/null; then
    print_success "Admin panel is healthy"
else
    print_error "Admin panel health check failed"
    journalctl -u "$SERVICE_NAME" -n 50
    exit 1
fi

# Check public site
DOMAIN=$(grep -E "^[^#]*\{" /etc/caddy/Caddyfile | head -1 | awk '{print $1}')
if [[ -n "$DOMAIN" ]] && curl -sf "https://$DOMAIN" > /dev/null; then
    print_success "Public site is accessible"
else
    print_info "Could not verify public site"
fi

# Clear caches
print_info "Clearing caches..."
if command -v redis-cli &> /dev/null; then
    redis-cli FLUSHDB || print_info "Redis cache clear failed (may not be configured)"
fi

# Log rotation
print_info "Rotating logs..."
logrotate -f /etc/logrotate.d/secref || true

# Final status
print_success "Deployment completed successfully!"

# Show service status
print_info "Service status:"
systemctl status "$SERVICE_NAME" --no-pager | head -10

# Show recent logs
print_info "Recent logs:"
journalctl -u "$SERVICE_NAME" -n 20 --no-pager

# Deployment summary
print_info "Deployment Summary:"
echo "  - Environment: $ENVIRONMENT"
echo "  - Deploy Path: $DEPLOY_DIR"
echo "  - Service: $SERVICE_NAME"
echo "  - Domain: ${DOMAIN:-not configured}"
echo "  - Backup: $BACKUP_DIR"

print_success "SecRef deployment complete!"