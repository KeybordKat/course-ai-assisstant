"""Local embedding generation using sentence-transformers."""
from typing import List
from sentence_transformers import SentenceTransformer
from src import config


class EmbeddingGenerator:
    """Generate embeddings locally using sentence-transformers."""

    def __init__(self, model_name: str = None):
        """
        Initialize the embedding generator.

        Args:
            model_name: Name of the sentence-transformer model
        """
        self.model_name = model_name or config.EMBEDDING_MODEL
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        print(f"✓ Model loaded (dimension: {self.model.get_sentence_embedding_dimension()})")

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str], show_progress: bool = True) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            show_progress: Whether to show progress bar

        Returns:
            List of embeddings
        """
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=show_progress,
            batch_size=32
        )
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        return self.model.get_sentence_embedding_dimension()


# Quick test
if __name__ == "__main__":
    generator = EmbeddingGenerator()

    # Test single embedding
    text = "This is a test sentence about machine learning."
    embedding = generator.embed_text(text)

    print(f"\n✓ Generated embedding")
    print(f"  Dimension: {len(embedding)}")
    print(f"  First 5 values: {embedding[:5]}")

    # Test batch
    texts = [
        "Machine learning is a subset of AI.",
        "Neural networks are inspired by the brain.",
        "Deep learning uses multiple layers."
    ]
    embeddings = generator.embed_batch(texts)
    print(f"\n✓ Generated {len(embeddings)} embeddings")