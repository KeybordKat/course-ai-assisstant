#!/bin/bash
# Start the FastAPI backend

echo "🚀 Starting FastAPI Backend..."
echo "================================"
echo ""
echo "📖 API Docs will be at: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/api/health"
echo ""

cd "$(dirname "$0")"
python src/api/main.py
