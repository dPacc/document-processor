#!/bin/bash

# Local development script to run NOVA Document Processor

echo "🚀 Starting NOVA Document Processor (Local Development)"
echo "============================================================"

# Check if ports are available
if lsof -Pi :8050 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Port 8050 is already in use"
    exit 1
fi

if lsof -Pi :3050 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Port 3050 is already in use"
    exit 1
fi

# Start server in background
echo "📡 Starting FastAPI server on port 8050..."
cd server
python -m uvicorn src.document_processor.api:app --host 0.0.0.0 --port 8050 --reload &
SERVER_PID=$!
cd ..

# Wait for server to be ready
echo "⏳ Waiting for server to be ready..."
sleep 10

# Check if server is running
if curl -s http://localhost:8050/health > /dev/null; then
    echo "✅ Server is running at http://localhost:8050"
    echo "📚 API Documentation: http://localhost:8050/docs"
else
    echo "❌ Server failed to start"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# Start client
echo "🎨 Starting React client on port 3050..."
cd client
export REACT_APP_API_URL=http://localhost:8050
npm start &
CLIENT_PID=$!
cd ..

echo ""
echo "🎉 NOVA Document Processor is running!"
echo "================================="
echo "🌐 Web Client: http://localhost:3050"
echo "🔧 API Server: http://localhost:8050"
echo "📚 API Docs:   http://localhost:8050/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $SERVER_PID 2>/dev/null
    kill $CLIENT_PID 2>/dev/null
    echo "✅ All services stopped"
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Wait for processes
wait