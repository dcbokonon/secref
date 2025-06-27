#!/bin/bash
# Quick setup script for SecRef development

echo "🔧 SecRef Quick Setup"
echo "===================="
echo ""

# Check for required tools
echo "Checking requirements..."
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }

echo "✓ Node.js found: $(node --version)"
echo "✓ Python found: $(python3 --version)"
echo ""

# Install Node dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
else
    echo "✓ Node modules already installed"
fi

# Set up Python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "✓ Python venv already exists"
fi

# Activate venv and install Python dependencies
echo "Installing Python dependencies..."
source venv/bin/activate 2>/dev/null || venv\\Scripts\\activate
pip install -q -r admin/requirements.txt
pip install -q -r tests/requirements.txt 2>/dev/null || true

# Set up .env file if it doesn't exist
if [ ! -f "admin/.env" ]; then
    echo ""
    echo "Setting up admin panel..."
    
    # Copy example env
    if [ -f ".env.example" ]; then
        cp .env.example admin/.env
    fi
    
    # Generate secret key
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    
    # Get admin password
    echo "Create an admin password for local development:"
    read -sp "Password: " ADMIN_PASS
    echo ""
    
    # Generate password hash
    HASH=$(python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('$ADMIN_PASS'))")
    
    # Create .env file
    cat > admin/.env << EOF
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=$SECRET_KEY
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=$HASH
DATABASE_PATH=../database/secref.db
EOF
    
    echo "✓ Admin panel configured"
else
    echo "✓ Admin panel already configured"
fi

# Initialize database
if [ ! -f "database/secref.db" ]; then
    echo "Initializing database..."
    python scripts/db_config_sqlite.py
    python scripts/import_json_to_sqlite.py
    echo "✓ Database initialized"
else
    echo "✓ Database already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start development:"
echo "  ./start.sh          # Start both services with tmux"
echo "  ./start_dev.py      # Start both services (no tmux)"
echo "  make dev-all        # Start both services"
echo ""
echo "Or start individually:"
echo "  make dev            # Start Astro only"
echo "  make admin          # Start admin panel only"
echo ""