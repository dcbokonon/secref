#!/bin/bash
# Start both Astro site and admin panel for local development

echo "🚀 Starting SecRef Development Environment"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if tmux is installed
if command -v tmux &> /dev/null; then
    echo -e "${GREEN}✓ Using tmux for split view${NC}"
    
    # Kill any existing secref session
    tmux kill-session -t secref 2>/dev/null
    
    # Create new tmux session with two panes
    tmux new-session -d -s secref -n main
    
    # Start Astro in first pane
    tmux send-keys -t secref:main.0 'npm run dev' C-m
    
    # Split window horizontally
    tmux split-window -h -t secref:main
    
    # Start Flask admin in second pane
    tmux send-keys -t secref:main.1 'cd admin && source ../venv/bin/activate 2>/dev/null || python3 -m venv ../venv && source ../venv/bin/activate && pip install -q -r requirements.txt && flask run' C-m
    
    # Attach to session
    echo ""
    echo -e "${BLUE}Starting services...${NC}"
    echo ""
    echo -e "${GREEN}📍 Astro Site:   ${YELLOW}http://localhost:4321${NC}"
    echo -e "${GREEN}📍 Admin Panel:  ${YELLOW}http://localhost:5001${NC}"
    echo ""
    echo "Press Ctrl+B then D to detach from tmux"
    echo "Run 'tmux attach -t secref' to reattach"
    echo ""
    sleep 2
    tmux attach -t secref
    
else
    echo -e "${YELLOW}tmux not found - starting in background${NC}"
    echo ""
    
    # Start Astro in background
    echo -e "${BLUE}Starting Astro site...${NC}"
    npm run dev > astro.log 2>&1 &
    ASTRO_PID=$!
    echo "Astro PID: $ASTRO_PID"
    
    # Set up Python venv if needed
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}Creating Python virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Start Flask admin in background
    echo -e "${BLUE}Starting admin panel...${NC}"
    cd admin
    source ../venv/bin/activate
    pip install -q -r requirements.txt
    flask run > ../admin.log 2>&1 &
    FLASK_PID=$!
    cd ..
    echo "Flask PID: $FLASK_PID"
    
    # Create stop script
    cat > stop.sh << EOF
#!/bin/bash
echo "Stopping services..."
kill $ASTRO_PID 2>/dev/null
kill $FLASK_PID 2>/dev/null
echo "Services stopped"
rm stop.sh
EOF
    chmod +x stop.sh
    
    echo ""
    echo -e "${GREEN}✅ Services started!${NC}"
    echo ""
    echo -e "${GREEN}📍 Astro Site:   ${YELLOW}http://localhost:4321${NC}"
    echo -e "${GREEN}📍 Admin Panel:  ${YELLOW}http://localhost:5001${NC}"
    echo ""
    echo "Run ./stop.sh to stop all services"
    echo "Check astro.log and admin.log for output"
    echo ""
    
    # Wait a bit for services to start
    sleep 3
    
    # Open browser if available
    if command -v open &> /dev/null; then
        open http://localhost:4321
    elif command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:4321
    fi
fi