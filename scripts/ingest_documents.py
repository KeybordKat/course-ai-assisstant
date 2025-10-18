"""Script to ingest PDF documents into the vector database."""
from pathlib import Path
from src import config


def main():
    """Main ingestion pipeline."""
    print("Document Ingestion Pipeline")
    print("=" * 50)

    # Check for PDFs
    pdf_files = list(config.PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"\n⚠ No PDF files found in {config.PDF_DIR}")
        print("Please add your course materials (PDFs) to the data/pdfs/ directory")
        return

    print(f"\nFound {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"  - {pdf.name}")

    print("\n📝 TODO: Implement document processing")
    print("  1. Extract text from PDFs")
    print("  2. Chunk documents")
    print("  3. Generate embeddings")
    print("  4. Store in ChromaDB")


if __name__ == "__main__":
    config.validate_config()
    main()