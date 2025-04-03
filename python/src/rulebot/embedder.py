from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        :param model_name: Name of the pretrained model from the Sentence-Transformers library.
        """
        self.model = SentenceTransformer(model_name)

    def embed(self, texts):
        """
        Generates embeddings for a list of texts or text chunks.
        :param texts: List of texts or text chunks.
        :return: numpy array with embedding vectors.
        """
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings
