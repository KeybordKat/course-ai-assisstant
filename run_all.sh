#!/bin/bash
# Start both API and UI in background

echo "🚀 Starting Course AI Assistant"
echo "================================"
echo ""

cd "$(dirname "$0")"

# Start API in background
echo "Starting API backend..."
python src/api/main.py > logs/api.log 2>&1 &
API_PID=$!
echo "✓ API started (PID: $API_PID)"

# Wait for API to be ready
echo "Waiting for API to initialize..."
sleep 5

# Start UI
echo "Starting Streamlit UI..."
streamlit run src/ui/app.py

# Cleanup on exit
trap "kill $API_PID 2>/dev/null" EXIT
