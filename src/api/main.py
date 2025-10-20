"""FastAPI backend for Course AI Assistant."""
import sys
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
from src.agent.core import CourseAgent, AgentResponse
from src.vector_store import VectorStore


# Global agent instance
agent: Optional[CourseAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agent on startup, cleanup on shutdown."""
    global agent
    print("🚀 Initializing Course AI Agent...")
    try:
        agent = CourseAgent()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        raise

    yield

    # Cleanup (if needed)
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Course AI Assistant API",
    description="AI assistant for course materials with RAG and web search",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class QuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str
    use_web_search: bool = True
    subject: Optional[str] = None  # Optional subject filter


class Citation(BaseModel):
    """Citation information."""
    source: str
    page: int
    text: str
    relevance: float


class AnswerResponse(BaseModel):
    """Response model for answers."""
    answer: str
    reasoning_steps: list[str]
    course_citations: list[Citation]
    web_sources: list[str]
    used_web_search: bool


class StatsResponse(BaseModel):
    """Database statistics."""
    total_chunks: int
    unique_sources: int
    sources: list[str]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    agent_ready: bool
    message: str


# Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Course AI Assistant API",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check if the system is ready."""
    if agent is None:
        return HealthResponse(
            status="error",
            agent_ready=False,
            message="Agent not initialized"
        )

    return HealthResponse(
        status="ok",
        agent_ready=True,
        message="System ready"
    )


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get vector database statistics."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    stats = agent.vector_store.get_stats()
    return StatsResponse(**stats)


@app.post("/api/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question to the agent.

    Args:
        request: Question and settings

    Returns:
        Answer with citations and reasoning
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        # Get answer from agent
        response = agent.answer_question(
            query=request.question,
            use_web=request.use_web_search,
            subject=request.subject
        )

        # Convert to API response format
        return AnswerResponse(
            answer=response.answer,
            reasoning_steps=response.reasoning_steps,
            course_citations=[
                Citation(
                    source=c.source,
                    page=c.page,
                    text=c.text,
                    relevance=c.relevance
                )
                for c in response.course_citations
            ],
            web_sources=response.web_sources,
            used_web_search=response.used_web_search
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.get("/api/sources")
async def get_sources():
    """Get list of all processed sources."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    sources = agent.vector_store.get_processed_sources()
    return {
        "sources": sorted(list(sources)),
        "count": len(sources)
    }


@app.get("/api/subjects")
async def get_subjects():
    """Get list of all subjects in the database."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    subjects = agent.vector_store.get_subjects()
    return {
        "subjects": subjects,
        "count": len(subjects)
    }


@app.post("/api/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    subject: str = Form(...)
):
    """
    Upload a PDF file to a specific subject.

    Args:
        file: PDF file to upload
        subject: Subject/folder name for the PDF

    Returns:
        Upload status and file info
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Import config for PDF directory
        from src import config

        # Create subject directory if it doesn't exist
        subject_dir = config.PDF_DIR / subject
        subject_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = subject_dir / file.filename

        # Check if file already exists
        if file_path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' already exists in subject '{subject}'"
            )

        # Write file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "status": "success",
            "message": f"File uploaded successfully to subject '{subject}'",
            "filename": file.filename,
            "subject": subject,
            "path": str(file_path),
            "note": "Run ingestion to add to database: python scripts/ingest_documents.py"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/ingest")
async def trigger_ingestion():
    """
    Trigger document ingestion for newly uploaded files.

    Note: This runs the ingestion script. The agent will need to be restarted
    after ingestion to load the new documents.

    Returns:
        Ingestion status
    """
    try:
        import subprocess
        from src import config

        # Run ingestion script
        result = subprocess.run(
            ["python", "scripts/ingest_documents.py"],
            cwd=str(config.PROJECT_ROOT),
            capture_output=True,
            text=True,
            input="y\n",  # Auto-confirm
            timeout=600  # 10 minute timeout
        )

        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Ingestion completed successfully",
                "note": "Please restart the API to load new documents",
                "output": result.stdout
            }
        else:
            return {
                "status": "error",
                "message": "Ingestion failed",
                "error": result.stderr
            }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Ingestion timed out (>10 minutes)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Starting Course AI Assistant API")
    print("=" * 60)
    print("\n📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/api/health")
    print("\n")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
