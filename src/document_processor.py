"""Document processing: Extract and chunk PDFs for RAG."""
from pathlib import Path
from typing import List, Dict, Any
import pdfplumber
from dataclasses import dataclass
from tqdm import tqdm

@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document."""
    text: str
    metadata: Dict[str, Any]
    chunk_id: str


class PDFProcessor:
    """Process PDF documents into chunks suitable for RAG."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize PDF processor.

        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Extract text from PDF with page-level metadata.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of dicts with text and metadata for each page
        """
        pages_data = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)

                # ADD PROGRESS BAR HERE
                for page_num, page in enumerate(tqdm(pdf.pages, desc="Extracting pages", unit="page"), start=1):
                    text = page.extract_text()

                    if text and text.strip():  # Only include pages with text
                        pages_data.append({
                            'text': text,
                            'page_number': page_num,
                            'source': pdf_path.name,
                            'total_pages': total_pages
                        })
        except Exception as e:
            print(f"Error processing {pdf_path.name}: {e}")
            return []

        return pages_data

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Split text into overlapping chunks (simple & fast).

        Args:
            text: The text to chunk
            metadata: Metadata to attach to each chunk

        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        text_length = len(text)
        chunk_num = 0

        # Simple sliding window - much faster than sentence detection
        start = 0
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk_text = text[start:end].strip()

            if chunk_text and len(chunk_text) > 50:  # Skip tiny chunks
                chunk_id = f"{metadata['source']}_page{metadata['page_number']}_chunk{chunk_num}"

                chunk_metadata = {
                    **metadata,
                    'chunk_id': chunk_id,
                    'chunk_index': chunk_num,
                    'char_start': start,
                    'char_end': end
                }

                chunks.append(DocumentChunk(
                    text=chunk_text,
                    metadata=chunk_metadata,
                    chunk_id=chunk_id
                ))

                chunk_num += 1

            # Move to next chunk with overlap
            start = end - self.chunk_overlap if end < text_length else text_length

        return chunks

    def process_pdf(self, pdf_path: Path) -> List[DocumentChunk]:
        """
        Process a PDF into chunks ready for embedding.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of DocumentChunk objects
        """
        print(f"Processing: {pdf_path.name}")

        # Extract text from all pages
        pages = self.extract_text_from_pdf(pdf_path)

        if not pages:
            print(f"  ⚠️  No text extracted from {pdf_path.name}")
            return []

        print(f"  Extracted {len(pages)} pages")

        # Chunk each page
        all_chunks = []
        for page_data in tqdm(pages, desc="Chunking pages", unit="page"):
            page_text = page_data['text']
            page_metadata = {
                'source': page_data['source'],
                'page_number': page_data['page_number'],
                'total_pages': page_data['total_pages']
            }

            chunks = self.chunk_text(page_text, page_metadata)
            all_chunks.extend(chunks)

        print(f"  Created {len(all_chunks)} chunks")
        return all_chunks

    def process_directory(self, directory: Path) -> List[DocumentChunk]:
        """
        Process all PDFs in a directory.

        Args:
            directory: Path to directory containing PDFs

        Returns:
            List of all DocumentChunk objects
        """
        pdf_files = list(directory.glob("*.pdf"))

        if not pdf_files:
            print(f"No PDF files found in {directory}")
            return []

        print(f"\nProcessing {len(pdf_files)} PDF files...\n")

        all_chunks = []
        for pdf_path in tqdm(pdf_files, desc="Processing PDFs", unit="file"):
            chunks = self.process_pdf(pdf_path)
            all_chunks.extend(chunks)

        print(f"\n✅ Total chunks created: {len(all_chunks)}")
        return all_chunks


# Quick test function
if __name__ == "__main__":
    from src import config

    processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
    chunks = processor.process_directory(config.PDF_DIR)

    if chunks:
        print("\n📄 Sample chunk:")
        print(f"Source: {chunks[0].metadata['source']}")
        print(f"Page: {chunks[0].metadata['page_number']}")
        print(f"Text preview: {chunks[0].text[:200]}...")