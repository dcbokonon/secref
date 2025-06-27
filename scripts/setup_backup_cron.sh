#!/bin/bash
# SecRef Backup Cron Setup Script
# Sets up automated daily database backups

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="${SCRIPT_DIR}/backup_database.py"
BACKUP_TIME="3:00"  # 3 AM daily
BACKUP_DIR="/var/backups/secref"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if backup script exists
if [[ ! -f "$BACKUP_SCRIPT" ]]; then
    print_error "Backup script not found: $BACKUP_SCRIPT"
    exit 1
fi

# Create backup directory
print_info "Creating backup directory: $BACKUP_DIR"
sudo mkdir -p "$BACKUP_DIR"
sudo chown "$USER:$USER" "$BACKUP_DIR"
print_success "Backup directory created"

# Create cron job
CRON_JOB="0 3 * * * cd $SCRIPT_DIR && /usr/bin/python3 $BACKUP_SCRIPT --backup-dir $BACKUP_DIR --keep 30 >> /var/log/secref-backup.log 2>&1"

print_info "Setting up cron job for daily backups at $BACKUP_TIME"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "backup_database.py"; then
    print_info "Backup cron job already exists. Updating..."
    # Remove existing job
    crontab -l | grep -v "backup_database.py" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
print_success "Cron job added"

# Create log rotation config
print_info "Setting up log rotation"
sudo tee /etc/logrotate.d/secref-backup > /dev/null <<EOF
/var/log/secref-backup.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 $USER $USER
}
EOF
print_success "Log rotation configured"

# Test backup
print_info "Running test backup..."
if python3 "$BACKUP_SCRIPT" --backup-dir "$BACKUP_DIR" --verbose; then
    print_success "Test backup successful"
else
    print_error "Test backup failed"
    exit 1
fi

# Show current cron jobs
print_info "Current backup cron job:"
crontab -l | grep "backup_database.py" || true

print_success "Backup automation setup complete!"
print_info "Backups will run daily at $BACKUP_TIME"
print_info "Backup location: $BACKUP_DIR"
print_info "Log file: /var/log/secref-backup.log"