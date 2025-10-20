"""Streamlit UI for Course AI Assistant."""
import streamlit as st
import requests
from typing import Optional
import time


# Configuration
API_URL = "http://localhost:8000"


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "use_web_search" not in st.session_state:
    st.session_state.use_web_search = True


def check_api_health() -> bool:
    """Check if the API is available."""
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        return response.status_code == 200 and response.json().get("agent_ready", False)
    except Exception:
        return False


def get_stats() -> Optional[dict]:
    """Get database statistics."""
    try:
        response = requests.get(f"{API_URL}/api/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def ask_question(question: str, use_web_search: bool) -> Optional[dict]:
    """Send question to API."""
    try:
        response = requests.post(
            f"{API_URL}/api/ask",
            json={
                "question": question,
                "use_web_search": use_web_search
            },
            timeout=300  # 5 minutes for first request (model loading)
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
    except requests.exceptions.Timeout:
        st.error("Request timed out. The question might be too complex.")
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
    return None


def format_citation(citation: dict) -> str:
    """Format a citation nicely."""
    return f"📄 **{citation['source']}** (Page {citation['page']}) - Relevance: {citation['relevance']:.2f}"


# Page config
st.set_page_config(
    page_title="Course AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .citation-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid #4CAF50;
        margin: 0.5rem 0;
    }
    .reasoning-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid #2196F3;
        margin: 0.5rem 0;
    }
    .web-source-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid #FF9800;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🎓 Course AI Assistant")
st.markdown("*Ask questions about your course materials*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # Check API health
    api_healthy = check_api_health()

    if api_healthy:
        st.success("✅ Connected to API")
    else:
        st.error("❌ API not available")
        st.warning("Please start the API server:\n```bash\npython src/api/main.py\n```")

    st.divider()

    # Web search toggle
    st.session_state.use_web_search = st.checkbox(
        "🌐 Enable Web Search",
        value=st.session_state.use_web_search,
        help="Search the web if course materials don't have enough information"
    )

    st.divider()

    # Database stats
    st.header("📊 Database Stats")
    if api_healthy:
        stats = get_stats()
        if stats:
            st.metric("Total Chunks", stats["total_chunks"])
            st.metric("Documents", stats["unique_sources"])

            with st.expander("📚 View Sources"):
                for source in stats["sources"]:
                    st.write(f"- {source}")
    else:
        st.info("Connect to API to view stats")

    st.divider()

    # Clear conversation
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # Info
    st.header("ℹ️ About")
    st.markdown("""
    This AI assistant uses:
    - 📚 Your course materials (RAG)
    - 🌐 Web search (optional)
    - 🧠 Local LLM (Ollama)

    **Tip:** The assistant will cite sources from your course materials!
    """)

# Main chat area
if not api_healthy:
    st.warning("⚠️ Please start the FastAPI backend first!")
    st.code("python src/api/main.py", language="bash")
    st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show additional info for assistant messages
        if message["role"] == "assistant" and "metadata" in message:
            metadata = message["metadata"]

            # Reasoning steps
            if metadata.get("reasoning_steps"):
                with st.expander("🧠 Reasoning Process"):
                    for step in metadata["reasoning_steps"]:
                        st.markdown(f"- {step}")

            # Citations
            if metadata.get("course_citations"):
                with st.expander(f"📚 Course Citations ({len(metadata['course_citations'])})"):
                    for i, citation in enumerate(metadata["course_citations"][:5], 1):
                        st.markdown(f"**{i}. {format_citation(citation)}**")
                        st.text(citation["text"][:200] + "..." if len(citation["text"]) > 200 else citation["text"])
                        st.divider()

            # Web sources
            if metadata.get("web_sources"):
                with st.expander(f"🌐 Web Sources ({len(metadata['web_sources'])})"):
                    for url in metadata["web_sources"]:
                        st.markdown(f"- [{url}]({url})")

# Chat input
if prompt := st.chat_input("Ask a question about your course materials..."):
    if not prompt.strip():
        st.error("Please enter a question")
        st.stop()

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from API
    with st.chat_message("assistant"):
        # Show appropriate spinner message
        if len(st.session_state.messages) <= 1:
            spinner_msg = "🤔 Thinking... (First question may take 30-60 seconds)"
        else:
            spinner_msg = "🤔 Thinking..."

        with st.spinner(spinner_msg):
            response = ask_question(prompt, st.session_state.use_web_search)

        if response:
            # Display answer
            st.markdown(response["answer"])

            # Store message with metadata
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["answer"],
                "metadata": response
            })

            # Show additional info
            with st.expander("🧠 Reasoning Process"):
                for step in response["reasoning_steps"]:
                    st.markdown(f"- {step}")

            if response["course_citations"]:
                with st.expander(f"📚 Course Citations ({len(response['course_citations'])})"):
                    for i, citation in enumerate(response["course_citations"][:5], 1):
                        st.markdown(f"**{i}. {format_citation(citation)}**")
                        st.text(citation["text"][:200] + "..." if len(citation["text"]) > 200 else citation["text"])
                        st.divider()

            if response["web_sources"]:
                with st.expander(f"🌐 Web Sources ({len(response['web_sources'])})"):
                    for url in response["web_sources"]:
                        st.markdown(f"- [{url}]({url})")

            st.rerun()
        else:
            st.error("Failed to get response from API")

# Footer
st.divider()
st.caption("🤖 Powered by Ollama, ChromaDB, and Claude Code")
