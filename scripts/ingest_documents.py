"""Script to ingest PDF documents into the vector database."""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src import config
from src.document_processor import PDFProcessor
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore
from tqdm import tqdm
import gc  # For garbage collection


def process_in_batches(chunks, embedding_gen, vector_store, batch_size=50):
    """
    Process chunks in batches to avoid memory issues.

    Args:
        chunks: List of all chunks
        embedding_gen: Embedding generator
        vector_store: Vector store
        batch_size: Number of chunks to process at once
    """
    total_chunks = len(chunks)
    num_batches = (total_chunks + batch_size - 1) // batch_size

    # Progress bar for overall batch processing
    batch_pbar = tqdm(total=num_batches, desc="Processing batches", unit="batch", position=0)

    # Progress bar for individual chunks
    chunk_pbar = tqdm(total=total_chunks, desc="Generating embeddings", unit="chunk", position=1)

    for i in range(0, total_chunks, batch_size):
        batch_end = min(i + batch_size, total_chunks)
        batch = chunks[i:batch_end]

        # Generate embeddings for this batch
        texts = [chunk.text for chunk in batch]
        embeddings = embedding_gen.embed_batch(texts, show_progress=False)  # Disable inner progress

        # Store this batch (with its own mini progress)
        vector_store.add_chunks(batch, embeddings)

        # Update progress bars
        batch_pbar.update(1)
        chunk_pbar.update(len(batch))

        # Free memory
        del texts
        del embeddings
        gc.collect()

    batch_pbar.close()
    chunk_pbar.close()
    print()  # Clean line after progress bars


def main():
    """Main ingestion pipeline."""
    print("=" * 60)
    print("Document Ingestion Pipeline - MEMORY EFFICIENT")
    print("=" * 60)

    # Step 1: Find PDFs (including in subdirectories)
    print("\n📂 Step 1: Finding PDF files...")
    pdf_files = list(config.PDF_DIR.glob("**/*.pdf"))  # Recursive search

    if not pdf_files:
        print(f"\n⚠️  No PDF files found in {config.PDF_DIR}")
        print("Please add your course materials (PDFs) to the data/pdfs/ directory")
        return

    print(f"✓ Found {len(pdf_files)} PDF files")
    for pdf in pdf_files:
        file_size = pdf.stat().st_size / (1024 * 1024)  # Size in MB
        print(f"  📄 {pdf.name} ({file_size:.1f} MB)")

    # Step 2: Check what's already processed
    print(f"\n📊 Step 2: Checking vector database...")
    vector_store = VectorStore()
    processed_sources = vector_store.get_processed_sources()

    if processed_sources:
        print(f"✓ Already processed: {len(processed_sources)} documents")
        for source in processed_sources:
            print(f"    - {source}")
    else:
        print("✓ Database is empty - ready for new documents")

    # Step 3: Find new PDFs
    new_pdfs = [pdf for pdf in pdf_files if pdf.name not in processed_sources]

    if not new_pdfs:
        print(f"\n✅ All PDFs already processed!")
        print(f"\nOptions:")
        print(f"  1. Add new PDFs to data/pdfs/")
        print(f"  2. To reprocess, delete data/vectordb/ and run again")

        # Show stats
        stats = vector_store.get_stats()
        print(f"\n📊 Current Vector Database Stats:")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Documents: {', '.join(stats['sources'])}")
        return

    print(f"\n📥 New PDFs to process: {len(new_pdfs)}")
    for pdf in new_pdfs:
        print(f"  📄 {pdf.name}")

    # Auto-confirm if running non-interactively, otherwise ask
    print(f"\n{'='*60}")
    import sys
    if sys.stdin.isatty():
        response = input("Process these new files? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return
    else:
        print("Auto-confirming (non-interactive mode)...")
        print("Processing files...")

    # Step 4: Initialize models
    print(f"\n{'='*60}")
    print("⚙️  Step 3: Initializing models...")
    print("=" * 60)

    processor = PDFProcessor(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    print("✓ Document processor ready")

    embedding_gen = EmbeddingGenerator()
    print("✓ Embedding generator ready")

    # Step 5: Process each PDF
    print(f"\n{'='*60}")
    print(f"📚 Step 4: Processing {len(new_pdfs)} PDF(s)")
    print("=" * 60)

    overall_pdf_progress = tqdm(total=len(new_pdfs), desc="Overall progress", unit="PDF", position=0)

    for pdf_num, pdf_path in enumerate(new_pdfs, 1):
        print(f"\n{'─'*60}")
        print(f"📄 PDF {pdf_num}/{len(new_pdfs)}: {pdf_path.name}")
        print(f"{'─'*60}")

        # Extract and chunk
        chunks = processor.process_pdf(pdf_path)

        if not chunks:
            print(f"⚠️  No chunks created from {pdf_path.name}")
            overall_pdf_progress.update(1)
            continue

        print(f"✓ Generated {len(chunks)} chunks")

        # Process in batches
        print(f"\n🔄 Generating embeddings and storing...")
        process_in_batches(
            chunks=chunks,
            embedding_gen=embedding_gen,
            vector_store=vector_store,
            batch_size=50
        )

        # Free memory
        del chunks
        gc.collect()

        print(f"✅ Completed: {pdf_path.name}")
        overall_pdf_progress.update(1)

    overall_pdf_progress.close()

    print(f"\n{'='*60}")
    print("🎉 All PDFs Processed!")
    print("=" * 60)

    # Step 6: Show final stats
    print(f"\n📊 Step 5: Final Statistics")
    print("=" * 60)

    stats = vector_store.get_stats()
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Unique documents: {stats['unique_sources']}")
    print(f"\n📚 Documents in database:")
    for source in stats['sources']:
        print(f"  ✓ {source}")

    print(f"\n{'='*60}")
    print("✅ SUCCESS! Your course materials are ready!")
    print("=" * 60)
    print(f"\n🚀 Next steps:")
    print(f"  1. Test retrieval: python src/vector_store.py")
    print(f"  2. Build the agent")
    print(f"  3. Create the UI")


if __name__ == "__main__":
    config.validate_config()
    main()