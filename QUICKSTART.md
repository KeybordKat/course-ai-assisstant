# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Start the Backend API

Open a terminal and run:
```bash
./run_api.sh
```

You should see:
```
🤖 Initializing Course AI Agent...
✓ Loaded 2515 chunks from 2 documents
✓ Using model: llama3.2
✓ Agent ready!
✅ Agent initialized successfully

INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!**

### Step 2: Start the UI

Open a **new terminal** and run:
```bash
./run_ui.sh
```

Your browser should automatically open to http://localhost:8501

### Step 3: Ask Questions!

In the chat interface, try asking:
- "What is propositional logic?"
- "Explain Turing machines"
- "What is a finite automaton?"

## 🎨 UI Features

### Main Chat
- Type your question in the input box at the bottom
- Press Enter or click to send
- View the answer with citations

### Sidebar
- **Enable/Disable Web Search**: Toggle whether to search the web for additional context
- **Database Stats**: See how many chunks and documents are loaded
- **View Sources**: See which PDFs are in your database
- **Clear Conversation**: Start fresh

### Answer Details
Each answer shows:
- 🧠 **Reasoning Process**: How the agent approached your question
- 📚 **Course Citations**: Excerpts from your PDFs with page numbers
- 🌐 **Web Sources**: Additional sources from the internet (if web search is enabled)

## 📖 Example Questions

Try these questions based on your loaded documents:

**Logic & Computation:**
- "What is the difference between syntax and semantics?"
- "Explain the concept of soundness and completeness"
- "What are the rules of natural deduction?"

**Theory of Computation:**
- "What is the Church-Turing thesis?"
- "Explain NP-completeness"
- "What is a context-free grammar?"

## 🛠️ Troubleshooting

### "API not available" error
- Make sure you ran `./run_api.sh` in a separate terminal
- Check that http://localhost:8000/api/health returns OK

### "Agent not initialized" error
- Run: `python scripts/ingest_documents.py`
- Make sure your PDFs are in `data/pdfs/`

### Slow responses
- First query is always slower (model initialization)
- Subsequent queries should be faster
- Disable web search for faster responses

### Port already in use
```bash
# Kill process on port 8000 (API)
lsof -ti:8000 | xargs kill -9

# Kill process on port 8501 (UI)
lsof -ti:8501 | xargs kill -9
```

## 🎯 Next Steps

1. **Add More Documents**: Place PDFs in `data/pdfs/` and run `python scripts/ingest_documents.py`
2. **Test the API**: Visit http://localhost:8000/docs for interactive API documentation
3. **Customize**: Edit `src/ui/app.py` to change the UI or `src/api/main.py` to add features

## 💡 Tips

- Keep both terminals open while using the app
- The agent remembers context within a conversation
- Citations show exactly where information came from in your PDFs
- Web search is helpful for current events or topics not in your documents

Enjoy your Course AI Assistant! 🎓
