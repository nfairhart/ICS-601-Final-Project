#!/bin/bash

# Document Management System - Startup Script
# This script starts both the backend (FastAPI) and frontend (FastHTML) servers

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

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Frontend stopped"
    fi
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Start Backend (FastAPI with Uvicorn)
echo -e "${BLUE}Starting Backend (FastAPI)...${NC}"
cd "$SCRIPT_DIR/backend"
python3 app.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
sleep 2

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}✗ Backend failed to start. Check logs/backend.log for details.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"
echo -e "  ${YELLOW}→${NC} API running at: http://localhost:8000"
echo ""

# Start Frontend (FastHTML)
echo -e "${BLUE}Starting Frontend (FastHTML)...${NC}"
cd "$SCRIPT_DIR/frontend"
python3 main.py > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 2

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}✗ Frontend failed to start. Check logs/frontend.log for details.${NC}"
    echo -e "${YELLOW}Stopping backend...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi
echo -e "${GREEN}✓${NC} Frontend started (PID: $FRONTEND_PID)"
echo -e "  ${YELLOW}→${NC} UI available at: http://localhost:5001"
echo ""

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Both servers are running!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}Access the application at:${NC}"
echo -e "  • Frontend UI: ${YELLOW}http://localhost:5001${NC}"
echo -e "  • Backend API: ${YELLOW}http://localhost:8000${NC}"
echo -e "  • API Docs: ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Monitor both processes
while true; do
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}✗ Backend process died unexpectedly!${NC}"
        echo -e "${YELLOW}Check logs/backend.log for details.${NC}"
        cleanup
    fi

    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}✗ Frontend process died unexpectedly!${NC}"
        echo -e "${YELLOW}Check logs/frontend.log for details.${NC}"
        cleanup
    fi

    sleep 2
done
