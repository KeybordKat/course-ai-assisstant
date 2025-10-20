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

if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = "all"


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


def get_subjects() -> list[str]:
    """Get available subjects."""
    try:
        response = requests.get(f"{API_URL}/api/subjects", timeout=5)
        if response.status_code == 200:
            return response.json().get("subjects", [])
    except Exception:
        pass
    return []


def ask_question(question: str, use_web_search: bool, subject: str = "all") -> Optional[dict]:
    """Send question to API."""
    try:
        response = requests.post(
            f"{API_URL}/api/ask",
            json={
                "question": question,
                "use_web_search": use_web_search,
                "subject": subject if subject != "all" else None
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


def upload_pdf(file, subject: str) -> Optional[dict]:
    """Upload a PDF file to a subject."""
    try:
        files = {"file": (file.name, file, "application/pdf")}
        data = {"subject": subject}

        response = requests.post(
            f"{API_URL}/api/upload",
            files=files,
            data=data,
            timeout=60
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None


def trigger_ingestion() -> Optional[dict]:
    """Trigger document ingestion."""
    try:
        response = requests.post(f"{API_URL}/api/ingest", timeout=600)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Ingestion failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Ingestion error: {str(e)}")
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

    # Subject selector
    st.header("📚 Subject Filter")
    if api_healthy:
        available_subjects = get_subjects()
        if available_subjects:
            # Add "All Subjects" option
            subject_options = ["all"] + available_subjects
            subject_labels = {
                "all": "All Subjects",
                **{s: s.replace("_", " ").title() for s in available_subjects}
            }

            selected_subject = st.selectbox(
                "Select Subject",
                options=subject_options,
                format_func=lambda x: subject_labels.get(x, x),
                index=subject_options.index(st.session_state.selected_subject) if st.session_state.selected_subject in subject_options else 0,
                help="Filter questions by subject - searches only relevant documents"
            )
            st.session_state.selected_subject = selected_subject

            if selected_subject != "all":
                st.info(f"📖 Searching only: **{subject_labels[selected_subject]}**")
        else:
            st.info("No subjects detected. Organize PDFs into subject folders.")
    else:
        st.info("Connect to API to select subjects")

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

    # Document Upload Section
    st.header("📤 Upload Documents")
    if api_healthy:
        with st.expander("➕ Add PDFs", expanded=False):
            # Subject input (existing or new)
            available_subjects = get_subjects()

            st.write("**Select or Create Subject:**")
            use_existing = st.radio(
                "Subject Type",
                ["Existing Subject", "New Subject"],
                horizontal=True,
                label_visibility="collapsed"
            )

            if use_existing == "Existing Subject" and available_subjects:
                subject_name = st.selectbox(
                    "Choose subject",
                    options=available_subjects,
                    label_visibility="collapsed"
                )
            else:
                subject_name = st.text_input(
                    "Subject name",
                    placeholder="e.g., Theory 4, Algorithms, etc.",
                    help="Enter a name for the new subject folder",
                    label_visibility="collapsed"
                )

            # File uploader
            uploaded_file = st.file_uploader(
                "Choose PDF file",
                type=['pdf'],
                help="Upload a PDF to add to your course materials",
                label_visibility="collapsed"
            )

            # Upload button
            if st.button("📤 Upload PDF", type="primary", use_container_width=True):
                if not subject_name or not subject_name.strip():
                    st.error("Please enter a subject name")
                elif not uploaded_file:
                    st.error("Please select a PDF file")
                else:
                    with st.spinner(f"Uploading {uploaded_file.name}..."):
                        result = upload_pdf(uploaded_file, subject_name.strip())
                        if result:
                            st.success(f"✅ {result['message']}")
                            st.info("💡 Click 'Process New Documents' below to add to database")

            st.divider()

            # Ingestion button
            st.write("**Process New Documents:**")
            if st.button("🔄 Process New Documents", use_container_width=True):
                with st.spinner("Processing documents... This may take several minutes"):
                    result = trigger_ingestion()
                    if result and result.get("status") == "success":
                        st.success("✅ Documents processed successfully!")
                        st.warning("⚠️ Please restart the app to load new documents")
                        st.code("Ctrl+C in terminal, then: ./start.sh")
                    elif result:
                        st.error(f"❌ {result.get('message', 'Processing failed')}")
    else:
        st.info("Connect to API to upload documents")

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
            response = ask_question(
                prompt,
                st.session_state.use_web_search,
                st.session_state.selected_subject
            )

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
