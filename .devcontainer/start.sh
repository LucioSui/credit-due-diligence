#!/bin/bash

echo ""
echo "========================================="
echo "  Starting Credit Due Diligence System"
echo "========================================="
echo ""

cd /workspace

# Start backend API server
echo "▶ Starting Backend API on port 8000..."
cd /workspace/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend dev server
echo "▶ Starting Frontend Dev on port 5173..."
cd /workspace/frontend
npx vite --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!

echo ""
echo "========================================="
echo "  Services started!"
echo "========================================="
echo "  Backend API:  http://localhost:8000"
echo "  API Docs:     http://localhost:8000/docs"
echo "  Frontend Dev: http://localhost:5173"
echo "========================================="
echo ""
echo "  PID Backend:  $BACKEND_PID"
echo "  PID Frontend: $FRONTEND_PID"
echo ""

# Wait for both processes
wait
