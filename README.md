# Course AI Assistant

An intelligent AI agent trained on course materials with web search capabilities and transparent reasoning.

## Features
- 📚 RAG system using course PDFs (textbooks, slides, examples)
- 🔍 Web search integration for current information
- 🧠 Transparent reasoning with step-by-step thought process
- 📝 Proper citation and source tracking
- 🎯 Hallucination prevention through fact-checking

## Tech Stack
- **LLM Framework:** LangChain
- **Vector DB:** ChromaDB
- **Embeddings:** Sentence Transformers
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **LLM:** Claude Sonnet / GPT-4

## Setup

### 1. Clone Repository
\`\`\`bash
git clone <your-repo-url>
cd course-ai-assistant
\`\`\`

### 2. Create Virtual Environment
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

### 3. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and add your API keys:
\`\`\`bash
cp .env.example .env
\`\`\`

### 5. Add Course Materials
Place your PDFs in `data/pdfs/`:
- Textbooks
- Lecture slides
- Example questions with answers

### 6. Ingest Documents
\`\`\`bash
python scripts/ingest_documents.py
\`\`\`

### 7. Run the Application
\`\`\`bash
# Option 1: Streamlit UI
streamlit run src/ui/app.py

# Option 2: API Server
uvicorn src.api.main:app --reload
\`\`\`

## Project Structure
\`\`\`
course-ai-assistant/
├── data/               # Data storage
├── src/                # Source code
│   ├── agent/         # Agent logic
│   ├── api/           # FastAPI backend
│   └── ui/            # Streamlit frontend
├── notebooks/          # Jupyter experiments
├── scripts/           # Utility scripts
└── tests/             # Unit tests
\`\`\`

## Development Roadmap
- [ ] Phase 1: Document processing and embedding
- [ ] Phase 2: Basic RAG pipeline
- [ ] Phase 3: Agent with web search
- [ ] Phase 4: Citation tracking
- [ ] Phase 5: UI development
- [ ] Phase 6: Hallucination prevention

## License
Private - For educational use only