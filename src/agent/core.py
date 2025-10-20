"""Core agent with RAG, reasoning, and web search."""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src import config
from src.vector_store import VectorStore
from src.embeddings import EmbeddingGenerator
from langchain_ollama import OllamaLLM
from duckduckgo_search import DDGS


@dataclass
class Citation:
    """Represents a citation from a source."""
    source: str
    page: int
    text: str
    relevance: float


@dataclass
class AgentResponse:
    """Response from the agent with reasoning and citations."""
    answer: str
    reasoning_steps: List[str]
    course_citations: List[Citation]
    web_sources: List[str]
    used_web_search: bool


class CourseAgent:
    """AI agent that answers questions using course materials and web search."""

    def __init__(self):
        """Initialize the agent."""
        print("🤖 Initializing Course AI Agent...")

        # Initialize components
        self.vector_store = VectorStore()
        self.embedding_gen = EmbeddingGenerator()
        self.llm = OllamaLLM(
            model=config.MODEL_NAME,
            temperature=config.TEMPERATURE
        )

        # Check database
        stats = self.vector_store.get_stats()
        if stats['total_chunks'] == 0:
            raise ValueError("Vector database is empty! Run: python scripts/ingest_documents.py")

        print(f"✓ Loaded {stats['total_chunks']} chunks from {stats['unique_sources']} documents")
        print(f"✓ Using model: {config.MODEL_NAME}")
        print("✓ Agent ready!")

    def retrieve_from_course(self, query: str, n_results: int = 5) -> List[Citation]:
        """
        Retrieve relevant chunks from course materials.

        Args:
            query: User's question
            n_results: Number of results to retrieve

        Returns:
            List of citations
        """
        results = self.vector_store.search(
            query=query,
            embedding_generator=self.embedding_gen,
            n_results=n_results
        )

        citations = []
        for doc, metadata, distance in zip(
                results['documents'],
                results['metadatas'],
                results['distances']
        ):
            citations.append(Citation(
                source=metadata['source'],
                page=metadata['page_number'],
                text=doc,
                relevance=1 - distance  # Convert distance to similarity
            ))

        return citations

    def search_web(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """
        Search the web using DuckDuckGo.

        Args:
            query: Search query
            max_results: Number of results

        Returns:
            List of search results
        """
        try:
            ddgs = DDGS()
            results = ddgs.text(query, max_results=max_results)
            return [
                {
                    'title': r.get('title', ''),
                    'url': r.get('href', ''),
                    'snippet': r.get('body', '')
                }
                for r in results
            ]
        except Exception as e:
            print(f"⚠️  Web search failed: {e}")
            return []

    def should_use_web_search(self, query: str, course_citations: List[Citation]) -> bool:
        """
        Decide if web search is needed.

        Args:
            query: User's question
            course_citations: Retrieved citations from course

        Returns:
            True if web search should be used
        """
        # Check if course materials are relevant enough
        if not course_citations:
            return True

        avg_relevance = sum(c.relevance for c in course_citations) / len(course_citations)

        # If best match is poor, use web search
        if avg_relevance < 0.3:
            return True

        # Check for current events keywords
        current_keywords = ['recent', 'latest', 'current', 'new', '2024', '2025', 'today']
        if any(keyword in query.lower() for keyword in current_keywords):
            return True

        return False

    def generate_reasoning(
            self,
            query: str,
            course_citations: List[Citation],
            web_results: List[Dict[str, str]]
    ) -> List[str]:
        """
        Generate step-by-step reasoning process.

        Args:
            query: User's question
            course_citations: Course material citations
            web_results: Web search results

        Returns:
            List of reasoning steps
        """
        steps = []

        steps.append(f"📚 Searched course materials and found {len(course_citations)} relevant chunks")

        if course_citations:
            best = course_citations[0]
            steps.append(f"📄 Most relevant: {best.source}, Page {best.page} (relevance: {best.relevance:.2f})")

        if web_results:
            steps.append(f"🌐 Searched web and found {len(web_results)} additional sources")

        steps.append("🧠 Synthesizing answer from available sources")

        return steps

    def answer_question(self, query: str, use_web: bool = True) -> AgentResponse:
        """
        Answer a question using course materials and optionally web search.

        Args:
            query: User's question
            use_web: Whether to use web search if needed

        Returns:
            AgentResponse with answer, reasoning, and citations
        """
        print(f"\n{'=' * 60}")
        print(f"Question: {query}")
        print("=" * 60)

        # Step 1: Retrieve from course materials
        print("📚 Searching course materials...")
        course_citations = self.retrieve_from_course(query, n_results=5)

        # Step 2: Decide if web search is needed
        web_results = []
        used_web = False

        if use_web and self.should_use_web_search(query, course_citations):
            print("🌐 Searching web for additional context...")
            web_results = self.search_web(query)
            used_web = len(web_results) > 0

        # Step 3: Generate reasoning
        reasoning_steps = self.generate_reasoning(query, course_citations, web_results)

        # Step 4: Build context for LLM
        context_parts = []

        if course_citations:
            context_parts.append("COURSE MATERIALS:\n")
            for i, citation in enumerate(course_citations[:3], 1):
                context_parts.append(
                    f"[Source {i}: {citation.source}, Page {citation.page}]\n"
                    f"{citation.text}\n"
                )

        if web_results:
            context_parts.append("\nWEB SEARCH RESULTS:\n")
            for i, result in enumerate(web_results, 1):
                context_parts.append(
                    f"[Web Source {i}: {result['title']}]\n"
                    f"{result['snippet']}\n"
                )

        context = "\n".join(context_parts)

        # Step 5: Create prompt with instructions
        prompt = f"""You are a helpful course assistant. Answer the question using the provided sources.

IMPORTANT INSTRUCTIONS:
- Base your answer primarily on the COURSE MATERIALS
- Use WEB SEARCH RESULTS only for additional context or current information
- ALWAYS cite your sources using [Source X, Page Y] format for course materials
- Be clear when information comes from web vs course materials
- If the course materials don't contain the answer, say so explicitly
- Explain concepts clearly and thoroughly

CONTEXT:
{context}

QUESTION: {query}

ANSWER (with citations):"""

        # Step 6: Generate answer
        print("🤖 Generating answer...")
        answer = self.llm.invoke(prompt)

        return AgentResponse(
            answer=answer,
            reasoning_steps=reasoning_steps,
            course_citations=course_citations,
            web_sources=[r['url'] for r in web_results],
            used_web_search=used_web
        )


# Quick test
if __name__ == "__main__":
    agent = CourseAgent()

    # Test question
    response = agent.answer_question("What is propositional logic")

    print("\n" + "=" * 60)
    print("REASONING PROCESS:")
    print("=" * 60)
    for step in response.reasoning_steps:
        print(f"  {step}")

    print("\n" + "=" * 60)
    print("ANSWER:")
    print("=" * 60)
    print(response.answer)

    print("\n" + "=" * 60)
    print("CITATIONS:")
    print("=" * 60)
    for citation in response.course_citations[:3]:
        print(f"  📄 {citation.source}, Page {citation.page}")