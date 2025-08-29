#!/bin/bash

echo "================================================"
echo "    Elder Care System Startup Script"
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js 16+ and try again"
    exit 1
fi

echo "✓ Python and Node.js detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies"
    exit 1
fi

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
cd eldercare-app
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Node.js dependencies"
    cd ..
    exit 1
fi
cd ..

echo ""
echo "================================================"
echo "    Dependencies installed successfully!"
echo "================================================"
echo ""
echo "Starting Elder Care System..."
echo ""
echo "1. Backend API will start on: http://localhost:8000"
echo "2. Frontend will start on: http://localhost:3000"  
echo "3. API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "Shutting down Elder Care System..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Services stopped."
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "Starting Backend API..."
source venv/bin/activate && python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start frontend in background
echo "Starting Frontend..."
cd eldercare-app && npm run dev &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

# Try to open browser (works on most Linux distributions and macOS)
echo "Opening Elder Care System in browser..."
sleep 3
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
elif command -v open &> /dev/null; then
    open http://localhost:3000
else
    echo "Please open http://localhost:3000 in your browser"
fi

echo ""
echo "================================================"
echo "    Elder Care System Started Successfully!"
echo "================================================"
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend App: http://localhost:3000"
echo "Caregiver Dashboard: http://localhost:3000/caregiver"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Services are running in the background."
echo "Press Ctrl+C to stop all services."
echo ""

# Wait for user to stop services
wait