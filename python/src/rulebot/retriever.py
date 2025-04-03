import faiss
from numpy import ndarray
import pickle

from .faiss_index_manager import FaissIndexManager
from .rule_book_retriever import RuleBookRetriever
from typing import Dict, Optional

MappingType = Dict[int, Dict[str, Optional[str]]]

class Retriever:
    def __init__(self,
                 embedding_dim: int,
                 top_k_chunks: int,
                 top_k_rules: int,
                 top_k_situations: int,
                 threshold: float,
                 situation_threshold: float,
                 rulebook_index: FaissIndexManager,
                 casebook_index: FaissIndexManager,
                 rulebook_mapping: MappingType,
                 casebook_mapping: MappingType,
                 rulebook_retriever: RuleBookRetriever):
        """
        Initializes the retrieval module with configuration values, FAISS indices, and preloaded mappings.

        :param embedding_dim: Dimension of the embeddings.
        :param top_k_chunks: Number of top chunks to retrieve from the rulebook index.
        :param top_k_rules: Number of top rules to consider after chunk grouping.
        :param top_k_situations: Number of top situations to retrieve from the casebook index.
        :param threshold: Similarity threshold for rule retrieval.
        :param situation_threshold: Similarity threshold for situation retrieval.
        :param rulebook_index: Loaded FAISS index manager for the rulebook.
        :param casebook_index: Loaded FAISS index manager for the casebook.
        :param rulebook_mapping: Mapping from chunk indices to rule metadata for the rulebook.
        :param casebook_mapping: Mapping from chunk indices to situation metadata for the casebook.
        :param rulebook_retriever: Component for retrieving rules from the rulebook.
        """
        self._embedding_dim = embedding_dim
        self._top_k_chunks = top_k_chunks
        self._top_k_rules = top_k_rules
        self._top_k_situations = top_k_situations
        self._threshold = threshold
        self._situation_threshold = situation_threshold

        self._faiss_manager = rulebook_index
        self._faiss_manager_casebook = casebook_index

        self._mapping = rulebook_mapping
        self._mapping_casebook = casebook_mapping

        self._rulebook_retriever = rulebook_retriever

    @staticmethod
    def load_mapping(path: str):
        with open(path, "rb") as f:
            return pickle.load(f)

    def retrieve_chunks(self, query_embedding: ndarray):
        """
        Performs a search in the FAISS index (rulebook) using the given user query embedding.
        :param query_embedding: The embeddings of the input question.
        :return: A list of tuples (chunk_info, similarity), each from the mapping.
        """
        distances, indices = self._faiss_manager.search(query_embedding, k=self._top_k_chunks)

        retrieved = []
        for sim, idx in zip(distances[0], indices[0]):
            chunk_info = self._mapping.get(idx, None)
            if chunk_info:
                retrieved.append({"rule_id": chunk_info["rule_id"], "similarity": sim})
        return retrieved

    def retrieve_rules_from_chunks(self, chunks: list) -> tuple:
        """
        Finds the individual rules corresponding to the provided rule chunks.

        :param chunks: List of chunk dictionaries. Each chunk contains the keys:
                       - "rule_id": the rule ID.
                       - "similarity": the similarity score of the chunk.
        :return: A list of dictionaries, each containing the following keys:
                 - "rule_id": The rule ID.
                 - "score_sum": Sum of the similarities of all associated chunks.
                 - "score_count": Number of chunks assigned to this rule.
                 - "rule_title": Rule name.
                 - "subrule_title": Subrule name.
                 - "text": Full rule text.
        """
        rules_dict = {}
        for chunk in chunks:
            rule_id = chunk.get("rule_id")
            similarity = chunk.get("similarity", 0)
            if rule_id not in rules_dict:
                rules_dict[rule_id] = {"score_sum": similarity, "score_count": 1}
            else:
                rules_dict[rule_id]["score_sum"] += similarity
                rules_dict[rule_id]["score_count"] += 1

        # Sort rules by similarity sum (descending)
        sorted_rules = sorted(rules_dict.items(), key=lambda item: item[1]["score_sum"], reverse=True)

        all_rules = []
        for rule_id, data in sorted_rules:
            rule = self._rulebook_retriever.get_rule_by_id(rule_id)
            all_rules.append({
                "rule_id": rule_id,
                "score_sum": data["score_sum"],
                "score_count": data["score_count"],
                "rule_title": rule["rule_title"],
                "subrule_title": rule["subrule_title"],
                "text": rule["text"],
            })

        # Filter rules exceeding the threshold and select the top-k
        top_rules_candidates = [rule for rule in all_rules if rule["score_sum"] > self._threshold]
        top_rules = top_rules_candidates[:self._top_k_rules]

        return all_rules, top_rules

    def retrieve_situations(self, query_embedding: ndarray):
        """
        Performs a search in the FAISS index (situation handbook) using the given user query embedding.
        :param query_embedding: The embeddings of the input question.
        :return: A list of tuples (chunk_info, similarity), each from the mapping.
        """
        distances, indices = self._faiss_manager_casebook.search(query_embedding, k=self._top_k_situations)

        retrieved = []
        for sim, idx in zip(distances[0], indices[0]):
            if sim >= self._situation_threshold:
                situation_info = self._mapping_casebook.get(idx, None)
                if situation_info:
                    retrieved.append({
                        "rule_id": situation_info["rule_id"],
                        "situation_id": situation_info["situation_id"],
                        "question": situation_info["question"],
                        "answer": situation_info["answer"],
                        "rule_reference": situation_info["rule_reference"],
                        "similarity": sim
                    })

        return retrieved