# Course AI Assistant - UI Guide

## Architecture

The application uses a **FastAPI + Streamlit** architecture:

```
┌─────────────────────┐
│  Streamlit UI       │  http://localhost:8501
│  (Frontend)         │
└──────────┬──────────┘
           │ REST API
           ↓
┌─────────────────────┐
│  FastAPI Backend    │  http://localhost:8000
│  (Business Logic)   │
│  - CourseAgent      │
│  - Vector Store     │
│  - Embeddings       │
└─────────────────────┘
```

## Quick Start

### Option 1: Run Both Services Separately (Recommended)

**Terminal 1 - Start the API Backend:**
```bash
./run_api.sh
# Or: python src/api/main.py
```

**Terminal 2 - Start the UI:**
```bash
./run_ui.sh
# Or: streamlit run src/ui/app.py
```

### Option 2: Run Everything at Once
```bash
./run_all.sh
```

## Accessing the Application

Once both services are running:

- **UI (Chat Interface)**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/health

## Features

### Chat Interface
- 💬 Ask questions about your course materials
- 📚 View citations from course documents
- 🧠 See reasoning process
- 🌐 Optional web search for additional context

### Sidebar Features
- ⚙️ Enable/disable web search
- 📊 View database statistics
- 📚 List all loaded documents
- 🗑️ Clear conversation history

### Response Information
Each answer includes:
1. **Answer**: AI-generated response
2. **Reasoning Steps**: How the agent approached the question
3. **Course Citations**: Relevant excerpts from your PDFs with page numbers
4. **Web Sources**: Additional web sources (if web search was used)

## API Endpoints

### `GET /api/health`
Check if the system is ready.

**Response:**
```json
{
  "status": "ok",
  "agent_ready": true,
  "message": "System ready"
}
```

### `GET /api/stats`
Get vector database statistics.

**Response:**
```json
{
  "total_chunks": 2515,
  "unique_sources": 2,
  "sources": ["document1.pdf", "document2.pdf"]
}
```

### `POST /api/ask`
Ask a question to the agent.

**Request:**
```json
{
  "question": "What is propositional logic?",
  "use_web_search": true
}
```

**Response:**
```json
{
  "answer": "...",
  "reasoning_steps": ["...", "..."],
  "course_citations": [
    {
      "source": "document.pdf",
      "page": 42,
      "text": "...",
      "relevance": 0.85
    }
  ],
  "web_sources": ["https://..."],
  "used_web_search": true
}
```

### `GET /api/sources`
Get list of all processed documents.

**Response:**
```json
{
  "sources": ["document1.pdf", "document2.pdf"],
  "count": 2
}
```

## Development

### Project Structure
```
src/
├── api/
│   ├── __init__.py
│   └── main.py          # FastAPI backend
├── ui/
│   ├── __init__.py
│   └── app.py           # Streamlit frontend
├── agent/
│   └── core.py          # Course agent logic
├── vector_store.py      # ChromaDB integration
├── embeddings.py        # Embedding generation
└── document_processor.py # PDF processing
```

### Adding New Features

#### Backend (API)
1. Add new endpoint in `src/api/main.py`
2. Define request/response models with Pydantic
3. Test at http://localhost:8000/docs

Example:
```python
@app.post("/api/new-feature")
async def new_feature(request: NewFeatureRequest):
    # Your logic here
    return {"result": "..."}
```

#### Frontend (UI)
1. Add new UI component in `src/ui/app.py`
2. Call the API endpoint using `requests`
3. Display results with Streamlit components

Example:
```python
def call_new_feature():
    response = requests.post(f"{API_URL}/api/new-feature", json={...})
    return response.json()

# In your Streamlit code:
if st.button("New Feature"):
    result = call_new_feature()
    st.write(result)
```

## Troubleshooting

### API Not Available
**Error:** `❌ API not available` in UI

**Solution:**
1. Make sure the API is running: `./run_api.sh`
2. Check API health: http://localhost:8000/api/health
3. Verify no port conflicts on port 8000

### Agent Not Initialized
**Error:** `Agent not initialized` or `Vector database is empty`

**Solution:**
1. Run document ingestion: `python scripts/ingest_documents.py`
2. Make sure PDFs are in `data/pdfs/`
3. Check that Ollama is running: `ollama list`

### Connection Timeout
**Error:** Request timed out

**Solution:**
- The question might be complex
- Check if Ollama is running and responsive
- Try disabling web search
- Make sure your LLM model is downloaded: `ollama pull llama3.2`

### Port Already in Use
**Error:** `Address already in use`

**Solution:**
```bash
# Find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Or for port 8501
lsof -ti:8501 | xargs kill -9
```

## Future Enhancements

Easy to add:
- 📤 Document upload via UI
- 💾 Conversation history export
- 👤 User authentication
- 📊 Analytics dashboard
- 🔄 Real-time streaming responses
- 📱 Mobile-friendly responsive design
- 🎨 Custom themes
- 🔍 Advanced search filters

## Tips

1. **Better Performance**: Keep the API running between questions
2. **Faster Responses**: Disable web search if not needed
3. **Debugging**: Check `http://localhost:8000/docs` for API testing
4. **Logs**: API logs appear in the terminal where you ran `run_api.sh`
