import json
import pickle

from embedder import Embedder
from faiss_index_manager import FaissIndexManager
from config import EmbeddingConfig


class SituationHandBookEmbeddingCreator:
    def __init__(self,
                 embedder_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 embedding_dim: int = 384):
        """
        Initializes the embedding creator for the situation handbook.
        :param embedder_model_name: Name of the SentenceTransformer model.
        :param embedding_dim: Dimension of the embeddings.
        """
        self.embedder = Embedder(model_name=embedder_model_name)
        self.embedding_dim = embedding_dim
        self.faiss_manager = FaissIndexManager(embedding_dim)

        print(f"Selected embedder model: {embedder_model_name}")

    def process_casebook(self, casebook_path: str,
                         index_path: str = "casebook_faiss_index.index",
                         mapping_path: str = "casebook_chunk_mapping.pkl"):
        """
        Processes the full casebook (situation handbook):
          - Loads the casebook from a JSON file.
          - Uses the full question text as a single chunk (no splitting into multiple chunks).
          - Creates embeddings for the full question text.
          - Stores metadata (rule_id, rule_title, subrule_title) in the mapping.
          - Adds embeddings to a FAISS index.

        :param casebook_path: Path to the JSON file with the casebook.
                              Expected format: A list of objects, e.g.
                              [{ "id": "1.1.", "rule_title": "...", "subrule_title": "...", "text": "..." }, ...]
        :param index_path: Path where the FAISS index will be saved.
        :param mapping_path: Path where the mapping (Pickle file) will be saved.
        :return: Tuple (mapping, embeddings)
        """
        with open(casebook_path, "r", encoding="utf-8") as f:
            situations = json.load(f)

        all_chunks = []
        mapping = {}
        current_index = 0

        for situation in situations:
            rule_id = situation.get("rule_id")
            situation_id = situation.get("situation_id")
            question_text = situation.get("question")
            answer_text = situation.get("answer")
            rule_reference = situation.get("rule_reference")

            all_chunks.append(question_text)
            mapping[current_index] = {
                "rule_id": rule_id,
                "situation_id": situation_id,
                "question": question_text,
                "answer": answer_text,
                "rule_reference": rule_reference,
            }
            current_index += 1

        print(f"Created {len(all_chunks)} chunks from {len(situations)} situations.")

        embeddings = self.embedder.embed(all_chunks)
        self.faiss_manager.add_embeddings(embeddings)
        self.faiss_manager.save_index(index_path)

        with open(mapping_path, "wb") as f:
            pickle.dump(mapping, f)
        print(f"Mapping saved to '{mapping_path}'.")

        return mapping, embeddings


if __name__ == "__main__":
    embedder_name = EmbeddingConfig["embedder_model_name"]
    casebook_path = EmbeddingConfig["casebook_path"]
    index_path = EmbeddingConfig["casebook_index_output_path"]
    mapping_path = EmbeddingConfig["casebook_chunk_mapping_path"]
    embedding_dim = EmbeddingConfig["embedding_dim"]

    creator = SituationHandBookEmbeddingCreator(
                                                embedder_model_name=embedder_name,
                                                embedding_dim=embedding_dim)

    creator.process_casebook(casebook_path=casebook_path,
                             index_path=index_path,
                             mapping_path=mapping_path)
