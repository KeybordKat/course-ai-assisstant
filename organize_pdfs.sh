#!/bin/bash
# Helper script to organize existing PDFs into subject folders

echo "📚 Organizing PDFs into Subject Folders"
echo "========================================"
echo ""

cd "$(dirname "$0")/data/pdfs"

# Create subject folders
echo "Creating subject folders..."
mkdir -p theory
mkdir -p logic
mkdir -p problems

# Move files (you can customize this based on your PDFs)
echo ""
echo "Moving PDFs to subject folders..."

# Theory files
if [ -f "Languages & Theory of Computation Introduction 4th Ed.pdf" ]; then
    mv "Languages & Theory of Computation Introduction 4th Ed.pdf" theory/
    echo "  ✓ Moved Theory of Computation to theory/"
fi

# Logic files
if [ -f "LogicInComputerScience copy.pdf" ]; then
    mv "LogicInComputerScience copy.pdf" logic/
    echo "  ✓ Moved Logic in Computer Science to logic/"
fi

# Problem sets
for file in combined_problems_solutions_week*.pdf; do
    if [ -f "$file" ]; then
        mv "$file" problems/
        echo "  ✓ Moved $file to problems/"
    fi
done

echo ""
echo "✅ Organization complete!"
echo ""
echo "Your structure now:"
tree -L 2 2>/dev/null || find . -maxdepth 2 -type f -name "*.pdf" | sort

echo ""
echo "⚠️  Next step: Re-ingest documents to add subject metadata"
echo "   Run: python scripts/ingest_documents.py"
