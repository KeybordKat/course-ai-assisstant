#!/bin/bash
# Setup script for new users

echo "🚀 Setting up Course AI Assistant"
echo "================================"

# Copy .env.example if .env doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "✓ Created .env"
else
    echo "✓ .env already exists"
fi

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
else
    echo "⚠️  Ollama not found"
    echo "   Install from: https://ollama.ai"
fi

# Check for models
if ollama list | grep -q "llama3.2"; then
    echo "✓ llama3.2 model ready"
else
    echo "📥 Pulling llama3.2 model..."
    ollama pull llama3.2
fi

echo ""
echo "✅ Setup complete!"
echo "Run: python scripts/test_install.py"