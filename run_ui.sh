#!/bin/bash
# Start the Streamlit UI

echo "🎨 Starting Streamlit UI..."
echo "============================"
echo ""
echo "📱 UI will open at: http://localhost:8501"
echo ""
echo "⚠️  Make sure the FastAPI backend is running first!"
echo "   Run: ./run_api.sh (in another terminal)"
echo ""

cd "$(dirname "$0")"
streamlit run src/ui/app.py
