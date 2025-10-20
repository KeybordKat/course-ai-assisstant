"""Vector database using ChromaDB for local storage."""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from tqdm import tqdm
from src import config
from src.embeddings import EmbeddingGenerator
from src.document_processor import DocumentChunk



class VectorStore:
    """Manage document embeddings in ChromaDB."""

    def __init__(self, collection_name: str = "course_documents"):
        """
        Initialize vector store.

        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.collection_name = collection_name

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(config.VECTORDB_DIR),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Course materials for RAG"}
        )

        print(f"✓ Vector store initialized: {collection_name}")
        print(f"  Location: {config.VECTORDB_DIR}")
        print(f"  Current documents: {self.collection.count()}")

    def add_chunks(
            self,
            chunks: List[DocumentChunk],
            embeddings: List[List[float]]
    ) -> None:
        """
        Add document chunks with their embeddings to the store.

        Args:
            chunks: List of DocumentChunk objects
            embeddings: Corresponding embeddings
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        if not chunks:
            print("No chunks to add")
            return

        # Prepare data for ChromaDB
        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        # Add to collection in batches with progress
        batch_size = 100
        num_batches = (len(chunks) + batch_size - 1) // batch_size

        with tqdm(total=num_batches, desc="Storing in database", unit="batch", position=2, leave=False) as pbar:
            for i in range(0, len(chunks), batch_size):
                end_idx = min(i + batch_size, len(chunks))

                self.collection.add(
                    ids=ids[i:end_idx],
                    embeddings=embeddings[i:end_idx],
                    documents=documents[i:end_idx],
                    metadatas=metadatas[i:end_idx]
                )

                pbar.update(1)

    def search(
        self,
        query: str,
        embedding_generator: EmbeddingGenerator,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            embedding_generator: Generator for query embedding
            n_results: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            Dict with documents, metadatas, and distances
        """
        # Generate query embedding
        query_embedding = embedding_generator.embed_text(query)

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )

        return {
            'documents': results['documents'][0] if results['documents'] else [],
            'metadatas': results['metadatas'][0] if results['metadatas'] else [],
            'distances': results['distances'][0] if results['distances'] else []
        }

    def clear(self) -> None:
        """Clear all documents from the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Course materials for RAG"}
        )
        print(f"✓ Cleared collection: {self.collection_name}")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        count = self.collection.count()

        # Get ALL data to check sources (not just a sample)
        if count > 0:
            all_data = self.collection.get()
            sources = set(m['source'] for m in all_data['metadatas'])
        else:
            sources = set()

        return {
            'total_chunks': count,
            'unique_sources': len(sources),
            'sources': list(sources)
        }

    def get_processed_sources(self) -> set:
        """Get list of already processed PDF sources."""
        count = self.collection.count()
        if count == 0:
            return set()

        # Get all metadata
        all_data = self.collection.get()
        sources = {m['source'] for m in all_data['metadatas']}
        return sources

    def has_source(self, source_name: str) -> bool:
        """Check if a source has already been processed."""
        return source_name in self.get_processed_sources()


# Quick test
if __name__ == "__main__":
    from embeddings import EmbeddingGenerator

    # Initialize
    vector_store = VectorStore()
    embedding_gen = EmbeddingGenerator()

    # Show stats
    stats = vector_store.get_stats()
    print(f"\n📊 Vector Store Stats:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Unique sources: {stats['unique_sources']}")
    if stats['sources']:
        print(f"  Sources: {', '.join(stats['sources'])}")