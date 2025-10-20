"""Comprehensive system tests for Course AI Assistant."""
import sys
from pathlib import Path
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.vector_store import VectorStore
from src.embeddings import EmbeddingGenerator
from src.document_processor import PDFProcessor, DocumentChunk
from src.agent.core import CourseAgent


class TestVectorStore:
    """Test vector store functionality."""

    def test_vector_store_initialization(self):
        """Test that vector store initializes correctly."""
        vs = VectorStore()
        assert vs is not None
        assert vs.collection is not None

    def test_get_stats(self):
        """Test getting database statistics."""
        vs = VectorStore()
        stats = vs.get_stats()

        assert 'total_chunks' in stats
        assert 'unique_sources' in stats
        assert 'sources' in stats
        assert isinstance(stats['total_chunks'], int)
        assert isinstance(stats['sources'], list)

    def test_get_subjects(self):
        """Test getting available subjects."""
        vs = VectorStore()
        subjects = vs.get_subjects()

        assert isinstance(subjects, list)
        # Should have "Theory 3" after ingestion
        if vs.collection.count() > 0:
            assert len(subjects) > 0

    def test_get_processed_sources(self):
        """Test getting list of processed sources."""
        vs = VectorStore()
        sources = vs.get_processed_sources()

        assert isinstance(sources, set)


class TestEmbeddings:
    """Test embedding generation."""

    def test_embedding_initialization(self):
        """Test that embedding generator initializes."""
        embed_gen = EmbeddingGenerator()
        assert embed_gen is not None
        assert embed_gen.model is not None
        assert embed_gen.dimension == 384

    def test_embed_text(self):
        """Test single text embedding."""
        embed_gen = EmbeddingGenerator()
        embedding = embed_gen.embed_text("This is a test")

        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)

    def test_embed_batch(self):
        """Test batch embedding."""
        embed_gen = EmbeddingGenerator()
        texts = ["Test 1", "Test 2", "Test 3"]
        embeddings = embed_gen.embed_batch(texts, show_progress=False)

        assert isinstance(embeddings, list)
        assert len(embeddings) == 3
        assert all(len(e) == 384 for e in embeddings)


class TestDocumentProcessor:
    """Test document processing."""

    def test_processor_initialization(self):
        """Test PDF processor initialization."""
        processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
        assert processor.chunk_size == 1000
        assert processor.chunk_overlap == 200

    def test_chunk_text(self):
        """Test text chunking."""
        processor = PDFProcessor(chunk_size=100, chunk_overlap=20)
        text = "This is a test. " * 50  # ~750 characters
        metadata = {'source': 'test.pdf', 'page_number': 1, 'subject': 'test'}

        chunks = processor.chunk_text(text, metadata)

        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(c, DocumentChunk) for c in chunks)
        assert all(c.metadata['subject'] == 'test' for c in chunks)


class TestAgent:
    """Test CourseAgent functionality."""

    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        try:
            return CourseAgent()
        except ValueError as e:
            if "Vector database is empty" in str(e):
                pytest.skip("Vector database is empty - run ingestion first")
            raise

    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly."""
        assert agent is not None
        assert agent.vector_store is not None
        assert agent.embedding_gen is not None
        assert agent.llm is not None

    def test_retrieve_from_course(self, agent):
        """Test retrieval from course materials."""
        results = agent.retrieve_from_course("What is a Turing machine?", n_results=3)

        assert isinstance(results, list)
        assert len(results) <= 3
        if len(results) > 0:
            assert hasattr(results[0], 'source')
            assert hasattr(results[0], 'page')
            assert hasattr(results[0], 'text')
            assert hasattr(results[0], 'relevance')

    def test_retrieve_with_subject_filter(self, agent):
        """Test retrieval with subject filter."""
        # Get available subjects
        subjects = agent.vector_store.get_subjects()

        if len(subjects) > 0:
            subject = subjects[0]
            results = agent.retrieve_from_course(
                "What is propositional logic?",
                n_results=3,
                subject=subject
            )

            assert isinstance(results, list)
            # Results should only be from the specified subject
            # (we can't easily test this without checking metadata)

    def test_should_use_web_search(self, agent):
        """Test web search decision logic."""
        # Mock some citations
        from src.agent.core import Citation

        # High relevance - shouldn't need web search
        good_citations = [
            Citation(source="test.pdf", page=1, text="relevant text", relevance=0.9)
        ]
        assert not agent.should_use_web_search("test query", good_citations)

        # Low relevance - should use web search
        bad_citations = [
            Citation(source="test.pdf", page=1, text="irrelevant", relevance=0.1)
        ]
        assert agent.should_use_web_search("test query", bad_citations)

        # Current events keywords - should use web search
        assert agent.should_use_web_search("What happened in 2025?", good_citations)


class TestSubjectFiltering:
    """Test subject-based filtering."""

    def test_subjects_are_detected(self):
        """Test that subjects are properly detected."""
        vs = VectorStore()
        subjects = vs.get_subjects()

        # After organizing PDFs into "Theory 3" folder
        if vs.collection.count() > 0:
            assert "Theory 3" in subjects or "general" in subjects

    def test_subject_metadata_exists(self):
        """Test that chunks have subject metadata."""
        vs = VectorStore()

        if vs.collection.count() > 0:
            sample = vs.collection.get(limit=10)
            metadatas = sample['metadatas']

            # All chunks should have subject metadata
            for meta in metadatas:
                assert 'subject' in meta
                assert meta['subject'] in ['Theory 3', 'general']


class TestAPI:
    """Test API endpoints (requires API to be running)."""

    @pytest.fixture
    def api_client(self):
        """Create test client."""
        try:
            from fastapi.testclient import TestClient
            from src.api.main import app
            return TestClient(app)
        except Exception as e:
            pytest.skip(f"Cannot create API client: {e}")

    def test_health_endpoint(self, api_client):
        """Test health check endpoint."""
        response = api_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "agent_ready" in data

    def test_stats_endpoint(self, api_client):
        """Test stats endpoint."""
        response = api_client.get("/api/stats")
        assert response.status_code in [200, 503]  # 503 if agent not ready

        if response.status_code == 200:
            data = response.json()
            assert "total_chunks" in data
            assert "unique_sources" in data

    def test_subjects_endpoint(self, api_client):
        """Test subjects endpoint."""
        response = api_client.get("/api/subjects")
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "subjects" in data
            assert isinstance(data["subjects"], list)


def test_integration_query():
    """Integration test: Full query pipeline."""
    try:
        agent = CourseAgent()

        # Test a simple query
        response = agent.answer_question(
            "What is a finite automaton?",
            use_web=False  # Disable web search for speed
        )

        assert response is not None
        assert hasattr(response, 'answer')
        assert hasattr(response, 'reasoning_steps')
        assert hasattr(response, 'course_citations')
        assert len(response.answer) > 0
        assert len(response.reasoning_steps) > 0

    except ValueError as e:
        if "Vector database is empty" in str(e):
            pytest.skip("Vector database is empty - run ingestion first")
        raise


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
