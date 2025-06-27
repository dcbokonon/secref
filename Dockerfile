# SecRef Multi-stage Dockerfile
# Optimized for security and small image size

# Stage 1: Build the Astro static site
FROM node:20-alpine AS builder

# Install dependencies for building
RUN apk add --no-cache python3 make g++

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the static site
RUN npm run build

# Stage 2: Python admin panel
FROM python:3.11-slim AS admin

# Security: Run as non-root user
RUN useradd -m -u 1000 secref && \
    mkdir -p /app/logs /app/database && \
    chown -R secref:secref /app

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY admin/requirements.txt ./admin/
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r admin/requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy admin application
COPY --chown=secref:secref admin/ ./admin/
COPY --chown=secref:secref scripts/ ./scripts/
COPY --chown=secref:secref database/schema_sqlite.sql ./database/

# Switch to non-root user
USER secref

# Create database if it doesn't exist
RUN python3 -c "import sqlite3; conn = sqlite3.connect('database/secref.db'); conn.executescript(open('database/schema_sqlite.sql').read()); conn.close()"

# Stage 3: Final image with Caddy
FROM caddy:2-alpine

# Install Python for admin panel
RUN apk add --no-cache python3 py3-pip supervisor

# Create non-root user
RUN adduser -D -u 1000 secref

# Copy built static files
COPY --from=builder --chown=secref:secref /app/dist /var/www/secref
COPY --chown=secref:secref public/ /var/www/secref/

# Copy admin application
COPY --from=admin --chown=secref:secref /app /admin

# Copy Caddy configuration
COPY --chown=caddy:caddy Caddyfile /etc/caddy/Caddyfile

# Copy supervisor configuration
COPY --chown=root:root supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create necessary directories
RUN mkdir -p /var/log/caddy /var/log/supervisor && \
    chown -R caddy:caddy /var/log/caddy && \
    chown -R secref:secref /admin/logs /admin/database

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]