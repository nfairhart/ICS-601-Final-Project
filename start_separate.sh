#!/bin/bash

# Document Management System - Startup Script (Separate Terminals)
# This script opens the backend and frontend in separate terminal windows

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Document Management System - Startup${NC}"
echo -e "${BLUE}  (Opening in separate terminal windows)${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please create a .env file with required environment variables.${NC}"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed!${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Environment checks passed"
echo ""

# Detect OS and open terminals accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo -e "${BLUE}Starting Backend in new Terminal window...${NC}"
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR/backend' && echo 'Starting FastAPI Backend...' && python3 app.py\""

    sleep 1

    echo -e "${BLUE}Starting Frontend in new Terminal window...${NC}"
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR/frontend' && echo 'Starting FastHTML Frontend...' && python3 main.py\""

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v gnome-terminal &> /dev/null; then
        echo -e "${BLUE}Starting Backend in new gnome-terminal...${NC}"
        gnome-terminal -- bash -c "cd '$SCRIPT_DIR/backend' && echo 'Starting FastAPI Backend...' && python3 app.py; exec bash"

        sleep 1

        echo -e "${BLUE}Starting Frontend in new gnome-terminal...${NC}"
        gnome-terminal -- bash -c "cd '$SCRIPT_DIR/frontend' && echo 'Starting FastHTML Frontend...' && python3 main.py; exec bash"
    elif command -v xterm &> /dev/null; then
        echo -e "${BLUE}Starting Backend in new xterm...${NC}"
        xterm -e "cd '$SCRIPT_DIR/backend' && echo 'Starting FastAPI Backend...' && python3 app.py" &

        sleep 1

        echo -e "${BLUE}Starting Frontend in new xterm...${NC}"
        xterm -e "cd '$SCRIPT_DIR/frontend' && echo 'Starting FastHTML Frontend...' && python3 main.py" &
    else
        echo -e "${RED}Error: No supported terminal emulator found!${NC}"
        echo -e "${YELLOW}Please use start.sh instead or open terminals manually.${NC}"
        exit 1
    fi
else
    echo -e "${RED}Error: Unsupported operating system!${NC}"
    echo -e "${YELLOW}Please use start.sh instead or open terminals manually.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Servers starting in separate windows!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}Access the application at:${NC}"
echo -e "  • Frontend UI: ${YELLOW}http://localhost:5001${NC}"
echo -e "  • Backend API: ${YELLOW}http://localhost:8000${NC}"
echo -e "  • API Docs: ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Close each terminal window individually to stop the servers.${NC}"
