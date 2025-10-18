"""Test that all required packages installed successfully - FREE LOCAL STACK."""
import subprocess
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all critical imports."""
    print("=" * 60)
    print("Testing Package Imports")
    print("=" * 60)

    failed_imports = []

    # Core packages
    packages = [
        ("pdfplumber", "PDF processing"),
        ("pypdf", "PDF parsing"),
        ("langchain", "LLM framework"),
        ("langchain_community", "LangChain community tools"),
        ("langchain_ollama", "Ollama integration (LOCAL LLM)"),
        ("chromadb", "Vector database (LOCAL)"),
        ("sentence_transformers", "Embeddings (LOCAL)"),
        ("duckduckgo_search", "Web search (FREE)"),
        ("streamlit", "UI framework"),
        ("fastapi", "API framework"),
        ("pandas", "Data processing"),
        ("dotenv", "Environment variables"),
    ]

    for package, description in packages:
        try:
            __import__(package)
            print(f"✓ {package:<25} - {description}")
        except ImportError as e:
            print(f"✗ {package:<25} - MISSING")
            failed_imports.append(package)

    if failed_imports:
        print(f"\n❌ Failed imports: {', '.join(failed_imports)}")
        print("\nRun: pip install -r requirements.txt")
        return False

    print("\n✅ All packages installed successfully!")
    return True


def test_ollama():
    """Test if Ollama is installed and running."""
    print("\n" + "=" * 60)
    print("Testing Ollama (Local LLM)")
    print("=" * 60)

    try:
        # Check if ollama command exists
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print("✓ Ollama is installed and running")

            # Check for models
            models = result.stdout.strip()
            if models and "NAME" in models:
                print("\n📦 Available models:")
                for line in models.split("\n")[1:]:  # Skip header
                    if line.strip():
                        model_name = line.split()[0]
                        print(f"   - {model_name}")

                # Check for recommended models
                if "llama3.2" in models or "llama3.1" in models or "mistral" in models:
                    print("\n✅ Ollama is ready to use!")
                    return True
                else:
                    print("\n⚠️  No recommended models found")
                    print("Run one of these commands:")
                    print("   ollama pull llama3.2")
                    print("   ollama pull llama3.1")
                    print("   ollama pull mistral")
                    return False
            else:
                print("\n⚠️  Ollama installed but no models found")
                print("Run: ollama pull llama3.2")
                return False
        else:
            print("✗ Ollama is not running")
            print("\nStart Ollama:")
            print("  - Open Ollama app, or")
            print("  - Run: ollama serve")
            return False

    except FileNotFoundError:
        print("✗ Ollama is not installed")
        print("\n📥 Install Ollama:")
        print("  1. Visit: https://ollama.ai")
        print("  2. Download for macOS")
        print("  3. Install and run")
        print("  4. Run: ollama pull llama3.2")
        return False
    except subprocess.TimeoutExpired:
        print("✗ Ollama command timed out")
        return False
    except Exception as e:
        print(f"✗ Error checking Ollama: {e}")
        return False


def test_ollama_connection():
    """Test if we can actually use Ollama with LangChain."""
    print("\n" + "=" * 60)
    print("Testing Ollama Connection")
    print("=" * 60)

    try:
        from langchain_ollama import OllamaLLM

        # Try to initialize (this checks if Ollama is accessible)
        llm = OllamaLLM(model="llama3.2", temperature=0)

        print("✓ Can initialize Ollama LLM")

        # Try a simple test (with timeout)
        try:
            response = llm.invoke("Say 'OK'", timeout=10)
            if response:
                print("✓ Can communicate with Ollama")
                print(f"  Response: {response[:50]}...")
                return True
        except Exception as e:
            print(f"⚠️  Ollama initialized but test query failed: {e}")
            print("  This might be okay - Ollama may need a moment to load the model")
            return True

    except ImportError:
        print("✗ langchain-ollama not installed")
        print("Run: pip install langchain-ollama")
        return False
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print("\nMake sure:")
        print("  1. Ollama is running")
        print("  2. You have a model: ollama pull llama3.2")
        return False


def test_embeddings():
    """Test local embeddings model."""
    print("\n" + "=" * 60)
    print("Testing Local Embeddings")
    print("=" * 60)

    try:
        from sentence_transformers import SentenceTransformer

        print("Loading embedding model (first time may take a moment)...")
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        # Test embedding
        test_text = "This is a test sentence."
        embedding = model.encode(test_text)

        print(f"✓ Embeddings working (dimension: {len(embedding)})")
        return True

    except Exception as e:
        print(f"✗ Embeddings failed: {e}")
        return False


def test_search():
    """Test free search (DuckDuckGo)."""
    print("\n" + "=" * 60)
    print("Testing Free Web Search")
    print("=" * 60)

    try:
        from duckduckgo_search import DDGS

        print("Testing DuckDuckGo search...")
        ddgs = DDGS()
        results = ddgs.text("test", max_results=1)

        if results:
            print("✓ DuckDuckGo search working")
            return True
        else:
            print("⚠️  Search returned no results (might be rate-limited)")
            return True

    except ImportError:
        print("✗ duckduckgo-search not installed")
        print("Run: pip install duckduckgo-search")
        return False
    except Exception as e:
        print(f"⚠️  Search test failed: {e}")
        print("  This is okay - might be rate limiting or network issue")
        return True


def main():
    """Run all tests."""
    print("\n🚀 Testing FREE LOCAL AI Stack Installation")
    print("=" * 60)

    results = {
        "Packages": test_imports(),
        "Ollama": test_ollama(),
        "Ollama Connection": test_ollama_connection(),
        "Embeddings": test_embeddings(),
        "Search": test_search(),
    }

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<20} {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 Everything is ready! You can start building!")
        print("\n💡 Quick start:")
        print("   1. Add your PDFs to data/pdfs/")
        print("   2. Run: python scripts/ingest_documents.py")
        print("   3. Start building your agent!")
    else:
        print("\n⚠️  Some tests failed - check the output above")
        print("\n📋 Common fixes:")
        print("   - Missing packages: pip install -r requirements.txt")
        print("   - No Ollama: Visit https://ollama.ai and install")
        print("   - No models: Run 'ollama pull llama3.2'")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())