import faiss
import numpy as np

class FaissIndexManager:
    def __init__(self, embedding_dim: int):
        """
        Initializes the FAISS index with the given embedding dimension.
        :param embedding_dim: Dimension of the embedding vectors.
        """
        self.embedding_dim = embedding_dim
        # We use an index for exact search with inner product (IP).
        self.index = faiss.IndexFlatIP(embedding_dim)

    def add_embeddings(self, embeddings: np.ndarray):
        """
        Adds a batch of embeddings to the index.
        :param embeddings: NumPy array [of shape: (num_vectors, embedding_dim)].
        """
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype("float32")

        # Normalize embeddings row-wise
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings_norm = embeddings / norms
        self.index.add(embeddings_norm)
        print(f"{embeddings_norm.shape[0]} vectors have been added to the FAISS index.")

    def save_index(self, index_path: str):
        """
        Saves the FAISS index to disk.
        :param index_path: Path to the index file (e.g., 'faiss_index.index').
        """
        faiss.write_index(self.index, index_path)
        print(f"FAISS index was saved to '{index_path}'.")

    def load_index(self, index_path: str):
        """
        Loads a FAISS index from disk.
        :param index_path: Path to the saved index file.
        """
        self.index = faiss.read_index(index_path)
        print(f"FAISS index was loaded from '{index_path}'.")

    def search(self, query_embeddings: np.ndarray, k: int = 5):
        """
        Searches the index and returns the k nearest neighbors.
        The query embeddings are also normalized.
        :param query_embeddings: NumPy array [of shape: (num_queries, embedding_dim)].
        :param k: Number of nearest neighbors to retrieve.
        :return: Tuple (distances, indices), both as NumPy arrays.
        """
        if query_embeddings.dtype != np.float32:
            query_embeddings = query_embeddings.astype("float32")

        # Normalize query embeddings
        query_norms = np.linalg.norm(query_embeddings, axis=1, keepdims=True)
        query_embeddings_norm = query_embeddings / query_norms
        distances, indices = self.index.search(query_embeddings_norm, k)
        return distances, indices
