#!/bin/bash
# Debug version - shows all output

echo "🚀 Starting Course AI Assistant (Debug Mode)"
echo "=============================================="
echo ""

cd "$(dirname "$0")"

# Kill any existing processes
echo "Cleaning up any existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8501 | xargs kill -9 2>/dev/null
sleep 2

# Start API with visible output
echo "📡 Starting FastAPI backend..."
echo "   (This will take 10-15 seconds to initialize)"
echo ""

python src/api/main.py &
API_PID=$!

echo "API PID: $API_PID"
echo ""
echo "⏳ Waiting for API to be ready..."

# Wait and check
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    echo "  Attempt $i/30..."
    sleep 1
done

# Test API
echo ""
echo "Testing API..."
curl -s http://localhost:8000/api/health | python -m json.tool 2>/dev/null || echo "API not responding"

echo ""
echo "================================"
echo "Now starting Streamlit UI..."
echo "================================"
echo ""
echo "Open your browser to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

streamlit run src/ui/app.py
