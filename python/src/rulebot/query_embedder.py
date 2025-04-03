import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
from .text_chunker import TextChunker


class QueryEmbedder:
    def __init__(self,
                 tokenizer_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 embedder_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 overlap: int = 1):
        """
        Initializes the query embedder with a SentenceTransformer model and a compatible Hugging Face tokenizer.
        A TextChunker is configured to automatically split long input queries into manageable chunks
        based on the model's token limit and optional sentence overlap.

        :param tokenizer_name: Name of the Hugging Face tokenizer to use.
        :param embedder_model_name: Name of the SentenceTransformer model.
        :param overlap: Number of overlapping sentences between consecutive chunks.
        """
        self.model = SentenceTransformer(embedder_model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.chunker = TextChunker(tokenizer=self.tokenizer, max_tokens=self.model.get_max_seq_length(), overlap=overlap)

    def embed_query(self, query_text: str) -> np.ndarray:
        """
        Embeds the input query. If the query exceeds the token limit, it is chunked.
        The final embedding is the mean of all chunk embeddings.

        :param query_text: The input user query string.
        :return: A normalized embedding vector of shape (1, embedding_dim).
        """
        # Chunk input if too long
        chunks = self.chunker.chunk_text(query_text)
        print("--------------------------------")
        print(f"Anzahl erzeugter Chunks aus Nutzereingabe (Frage): {len(chunks)}")

        # Encode all chunks
        chunk_embeddings = self.model.encode(chunks, show_progress_bar=False)

        # Average the embeddings
        mean_embedding = np.mean(chunk_embeddings, axis=0)

        # Normalize the vector
        norm = np.linalg.norm(mean_embedding)
        normalized_embedding = mean_embedding / norm

        # Reshape to 2D array for FAISS
        return normalized_embedding.reshape(1, -1).astype("float32")
