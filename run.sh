#!/bin/bash

# Start backend API on port 8000
echo "Starting Backend API on http://localhost:8000..."
cd "$(dirname "$0")"
.venv/bin/python -m uvicorn backend.app:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend on port 5001
echo "Starting Frontend on http://localhost:5001..."
.venv/bin/python -m uvicorn frontend.main:app --reload --port 5001 &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "Services running:"
echo "  Backend API:  http://localhost:8000/docs"
echo "  Frontend:     http://localhost:5001"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
