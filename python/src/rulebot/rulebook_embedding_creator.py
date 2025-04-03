import json
import pickle
from transformers import AutoTokenizer

from text_chunker import TextChunker
from embedder import Embedder
from faiss_index_manager import FaissIndexManager
from config import EmbeddingConfig

class RuleBookEmbeddingCreator:
    def __init__(self,
                 tokenizer_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 embedder_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 overlap: int = 1,
                 embedding_dim: int = 384):
        """
        Initializes the embedding creator for the rulebook.
        :param tokenizer_name: Name of the Hugging Face tokenizer.
        :param embedder_model_name: Name of the SentenceTransformer model.
        :param overlap: Number of overlapping sentences between chunks.
        :param embedding_dim: Dimension of the embeddings.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.embedder = Embedder(model_name=embedder_model_name)
        self.chunker = TextChunker(self.tokenizer, max_tokens=self.embedder.model.get_max_seq_length(), overlap=overlap)
        self.embedding_dim = embedding_dim
        self.faiss_manager = FaissIndexManager(embedding_dim)

        print(f"Selected tokenizer model: {tokenizer_name}")
        print(f"Selected embedder model: {embedder_model_name}")

    def process_rulebook(self, rulebook_path: str,
                         index_path: str = "rulebook_faiss_index.index",
                         mapping_path: str = "rulebook_chunk_mapping.pkl"):
        """
        Processes the full rulebook:
          - Loads the rulebook from a JSON file.
          - Splits only the rule text into chunks.
          - Creates embeddings only for the rule text.
          - Stores metadata (rule ID, title, etc.) in the mapping.
          - Adds the embeddings to a FAISS index.

        :param rulebook_path: Path to the JSON rulebook file.
                              Expected format: A list of dicts, e.g.
                              [{ "id": "1.1.", "rule_title": "...", "subrule_title": "...", "text": "..." }, ...]
        :param index_path: Path where the FAISS index will be saved.
        :param mapping_path: Path where the mapping (Pickle file) will be saved.
        :return: Tuple (mapping, embeddings)
        """
        # Lade das Regelbuch (JSON-Datei)
        with open(rulebook_path, "r", encoding="utf-8") as f:
            rules = json.load(f)

        all_chunks = []
        mapping = {}  # Mapping: globaler Index -> dict { "rule_id", "chunk_text", "rule_name", "subrule_name" }
        current_index = 0

        for rule in rules:
            rule_id = rule.get("id", "")
            rule_text = rule.get("text", "")

            if not rule_text.strip():
                continue

            chunks = self.chunker.chunk_text(rule_text)
            for chunk in chunks:
                all_chunks.append(chunk)
                mapping[current_index] = {
                    "rule_id": rule_id,
                    "chunk_text": chunk,
                    "rule_title": rule.get("rule_title", None),
                    "subrule_title": rule.get("subrule_title", None)
                }
                current_index += 1

        print(f"Created {len(all_chunks)} chunks from {len(rules)} rules.")

        embeddings = self.embedder.embed(all_chunks)
        self.faiss_manager.add_embeddings(embeddings)
        self.faiss_manager.save_index(index_path)

        with open(mapping_path, "wb") as f:
            pickle.dump(mapping, f)
        print(f"Mapping saved to '{mapping_path}'.")

        return mapping, embeddings


if __name__ == "__main__":
    tokenizer_name = EmbeddingConfig["tokenizer_model_name"]
    embedder_name = EmbeddingConfig["embedder_model_name"]
    rulebook_path = EmbeddingConfig["rulebook_path"]
    index_path = EmbeddingConfig["index_output_path"]
    mapping_path = EmbeddingConfig["chunk_mapping_path"]
    overlap = EmbeddingConfig["overlap"]
    embedding_dim = EmbeddingConfig["embedding_dim"]

    creator = RuleBookEmbeddingCreator(tokenizer_name=tokenizer_name,
                                       embedder_model_name=embedder_name,
                                       overlap=overlap,
                                       embedding_dim=embedding_dim)

    creator.process_rulebook(rulebook_path=rulebook_path,
                             index_path=index_path,
                             mapping_path=mapping_path)
