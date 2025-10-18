"""Test that all required packages installed successfully."""


def test_imports():
    """Test all critical imports."""
    try:
        print("Testing imports...")

        import pdfplumber
        print("✓ pdfplumber")

        import pypdf
        print("✓ pypdf")

        import langchain
        print("✓ langchain")

        import chromadb
        print("✓ chromadb")

        import sentence_transformers
        print("✓ sentence_transformers")

        import streamlit
        print("✓ streamlit")

        import fastapi
        print("✓ fastapi")

        import pandas
        print("✓ pandas")

        print("\n✅ All packages installed successfully!")
        print("\nYou're ready to start building!")

    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        print("Run: pip install -r requirements.txt")


if __name__ == "__main__":
    test_imports()