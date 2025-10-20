"""FastAPI backend for Course AI Assistant."""
import sys
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
