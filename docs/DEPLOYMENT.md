# SecRef Deployment Guide

## Overview

This guide covers deploying SecRef to production using various methods. SecRef is designed to be secure, scalable, and easy to deploy.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Deployment Methods](#deployment-methods)
   - [Docker Deployment](#docker-deployment)
   - [Manual Deployment](#manual-deployment)
   - [Kubernetes Deployment](#kubernetes-deployment)
4. [Security Hardening](#security-hardening)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Ubuntu 22.04 LTS or similar Linux distribution
- **CPU**: 2+ cores recommended
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 10GB minimum
- **Network**: Public IP with ports 80/443 available

### Software Requirements

- Docker 24.0+ and Docker Compose 2.0+ (for containerized deployment)
- Python 3.11+ (for manual deployment)
- Node.js 20+ and npm 10+ (for building frontend)
- Git for source code management

### Domain & SSL

- Valid domain name pointing to server IP
- SSL certificate (auto-generated with Caddy)

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/dcbokonon/secref.git
cd secref
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Generate secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate admin password hash
python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-secure-password'))"

# Edit .env file with your values
nano .env
```

Required environment variables:

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-generated-secret-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your-generated-hash

# Database
SECREF_DB_PATH=/path/to/database/secref.db

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your-redis-password

# Backup Configuration
BACKUP_DIR=/var/backups/secref
BACKUP_SCHEDULE="0 3 * * *"  # 3 AM daily
```

## Deployment Methods

### Docker Deployment (Recommended)

#### 1. Build and Deploy

```bash
# Build the application
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 2. SSL Configuration

Edit `Caddyfile` to use your domain:

```caddyfile
yourdomain.com {
    # ... existing configuration
}
```

#### 3. Database Initialization

```bash
# Initialize database (if not exists)
docker-compose exec secref python3 /admin/scripts/init_db.py

# Import initial data
docker-compose exec secref python3 /admin/scripts/import_json.py
```

### Manual Deployment

#### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm caddy

# Create application user
sudo useradd -r -s /bin/bash -m -d /opt/secref secref

# Clone repository
sudo -u secref git clone https://github.com/dcbokonon/secref.git /opt/secref
cd /opt/secref
```

#### 2. Python Environment

```bash
# Create virtual environment
sudo -u secref python3.11 -m venv venv

# Activate and install dependencies
sudo -u secref bash -c "source venv/bin/activate && pip install -r requirements.txt"
sudo -u secref bash -c "source venv/bin/activate && pip install -r admin/requirements.txt"
```

#### 3. Build Frontend

```bash
# Install Node dependencies
sudo -u secref npm ci

# Build static site
sudo -u secref npm run build
```

#### 4. Configure Systemd Service

```bash
# Copy service files
sudo cp scripts/secref-admin.service /etc/systemd/system/
sudo cp scripts/secref-backup.service /etc/systemd/system/
sudo cp scripts/secref-backup.timer /etc/systemd/system/

# Edit service files with correct paths
sudo nano /etc/systemd/system/secref-admin.service

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable --now secref-admin
sudo systemctl enable --now secref-backup.timer
```

#### 5. Configure Caddy

```bash
# Copy Caddyfile
sudo cp Caddyfile /etc/caddy/Caddyfile

# Edit with your domain
sudo nano /etc/caddy/Caddyfile

# Reload Caddy
sudo systemctl reload caddy
```

### Kubernetes Deployment

#### 1. Create Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: secref
```

#### 2. ConfigMap for Environment

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: secref-config
  namespace: secref
data:
  FLASK_ENV: "production"
  SECREF_DB_PATH: "/data/secref.db"
```

#### 3. Secret for Sensitive Data

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: secref-secret
  namespace: secref
type: Opaque
stringData:
  SECRET_KEY: "your-secret-key"
  ADMIN_PASSWORD_HASH: "your-hash"
```

#### 4. Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secref
  namespace: secref
spec:
  replicas: 2
  selector:
    matchLabels:
      app: secref
  template:
    metadata:
      labels:
        app: secref
    spec:
      containers:
      - name: secref
        image: secref:latest
        ports:
        - containerPort: 80
        - containerPort: 443
        envFrom:
        - configMapRef:
            name: secref-config
        - secretRef:
            name: secref-secret
        volumeMounts:
        - name: data
          mountPath: /data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: secref-data
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

### 2. Fail2ban Setup

```bash
# Install fail2ban
sudo apt install fail2ban

# Create jail configuration
sudo nano /etc/fail2ban/jail.local
```

Add:
```ini
[secref-admin]
enabled = true
port = http,https
filter = secref-admin
logpath = /var/log/caddy/secref.log
maxretry = 5
bantime = 3600
```

### 3. Security Headers

Already configured in Caddyfile:
- Strict-Transport-Security
- X-Content-Type-Options
- X-Frame-Options
- Content-Security-Policy
- Permissions-Policy

### 4. Database Encryption

```bash
# Encrypt database at rest
sudo apt install cryptsetup

# Create encrypted volume
sudo cryptsetup luksFormat /dev/sdb1
sudo cryptsetup open /dev/sdb1 secref-data
sudo mkfs.ext4 /dev/mapper/secref-data
sudo mount /dev/mapper/secref-data /var/lib/secref
```

### 5. Audit Logging

```bash
# Install auditd
sudo apt install auditd

# Add rules for SecRef
sudo auditctl -w /opt/secref -p wa -k secref_changes
sudo auditctl -w /var/lib/secref -p wa -k secref_data
```

## Monitoring & Maintenance

### 1. Health Checks

```bash
# Check application health
curl https://yourdomain.com/admin/api/health

# Check service status
sudo systemctl status secref-admin
sudo systemctl status caddy
```

### 2. Log Management

```bash
# View application logs
sudo journalctl -u secref-admin -f

# View Caddy logs
sudo tail -f /var/log/caddy/secref.log

# Setup log rotation
sudo nano /etc/logrotate.d/secref
```

### 3. Backup Verification

```bash
# List backups
python3 scripts/backup_database.py --list

# Verify latest backup
python3 scripts/backup_database.py --verify /var/backups/secref/latest.db.gz

# Test restore (to different location)
python3 scripts/backup_database.py --restore /var/backups/secref/latest.db.gz --target /tmp/test.db
```

### 4. Monitoring Setup

#### Prometheus Metrics

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'secref'
    static_configs:
      - targets: ['localhost:5001']
    metrics_path: '/admin/metrics'
```

#### Grafana Dashboard

Import the SecRef dashboard from `monitoring/grafana-dashboard.json`

### 5. Updates & Upgrades

```bash
# Backup before update
docker-compose exec secref python3 scripts/backup_database.py

# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose down
docker-compose up -d

# Run migrations if needed
docker-compose exec secref python3 scripts/migrate.py
```

## Troubleshooting

### Common Issues

#### 1. Database Locked

```bash
# Stop services
docker-compose down

# Check for stale locks
lsof /path/to/secref.db

# Restart services
docker-compose up -d
```

#### 2. SSL Certificate Issues

```bash
# Check Caddy logs
docker-compose logs caddy

# Force certificate renewal
docker-compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```

#### 3. Permission Issues

```bash
# Fix ownership
sudo chown -R secref:secref /opt/secref
sudo chmod -R 755 /opt/secref
sudo chmod 600 /opt/secref/.env
```

#### 4. Memory Issues

```bash
# Check memory usage
docker stats

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Debug Mode (Development Only)

```bash
# Enable debug mode temporarily
export FLASK_DEBUG=True
export FLASK_ENV=development

# Run with verbose logging
python3 admin/app.py --debug
```

### Performance Tuning

#### 1. Database Optimization

```sql
-- Vacuum and analyze
VACUUM;
ANALYZE;

-- Check indexes
.indexes resources
```

#### 2. Caching Configuration

```python
# In admin/config.py
CACHE_TYPE = "redis"
CACHE_REDIS_URL = "redis://localhost:6379/0"
CACHE_DEFAULT_TIMEOUT = 300
```

#### 3. CDN Integration

```caddyfile
# In Caddyfile
header {
    Cache-Control "public, max-age=31536000"
}
```

## Support

- GitHub Issues: https://github.com/dcbokonon/secref/issues
- Documentation: https://secref.org/docs
- Email: support@secref.org

## Security Contacts

For security issues, please see [SECURITY.md](../SECURITY.md) or email security@secref.org