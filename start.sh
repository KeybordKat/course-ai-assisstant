#!/bin/bash
# Single script to run the entire Course AI Assistant

echo "🚀 Starting Course AI Assistant"
echo "================================"
echo ""

cd "$(dirname "$0")"

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        echo "  ✓ API stopped"
    fi
    if [ ! -z "$UI_PID" ]; then
        kill $UI_PID 2>/dev/null
        echo "  ✓ UI stopped"
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start API in background
echo "📡 Starting FastAPI backend..."
python src/api/main.py > logs/api.log 2>&1 &
API_PID=$!
echo "  ✓ API started (PID: $API_PID, logs: logs/api.log)"

# Wait for API to be ready
echo ""
echo "⏳ Waiting for API to initialize..."
sleep 8

# Check if API is healthy
API_HEALTHY=false
for i in {1..10}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        API_HEALTHY=true
        break
    fi
    sleep 1
done

if [ "$API_HEALTHY" = false ]; then
    echo "❌ API failed to start. Check logs/api.log for details"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo "  ✓ API is ready at http://localhost:8000"
echo ""

# Start Streamlit UI
echo "🎨 Starting Streamlit UI..."
echo "  ✓ UI will open at http://localhost:8501"
echo ""
echo "================================"
echo "✅ Both services are running!"
echo "================================"
echo ""
echo "📖 API Docs: http://localhost:8000/docs"
echo "🎨 Chat UI: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

streamlit run src/ui/app.py

# Cleanup when streamlit exits
cleanup
