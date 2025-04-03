import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from config import EmbeddingConfig
from sklearn.metrics.pairwise import cosine_similarity
import re

class SemanticSearcher:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(EmbeddingConfig["model_name"])
        self.model = AutoModel.from_pretrained(EmbeddingConfig["model_name"])
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        data = np.load(EmbeddingConfig["embedding_output_path"] + ".npz", allow_pickle=True)
        self.rule_embeddings = data["embeddings"]
        self.rule_ids = data["ids"].tolist()

        with open(EmbeddingConfig["rulebook_path"], "r", encoding="utf-8") as f:
            rules_data = json.load(f)
            self.rules_text = [rule["text"] for rule in rules_data if rule["text"]]

    def embed_query(self, query):
        inputs = self.tokenizer(
            query,
            padding=EmbeddingConfig["padding"],
            truncation=True,
            max_length=EmbeddingConfig["max_length"],
            return_tensors="pt"
        ).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            query_embedding = outputs.last_hidden_state.mean(dim=1)
        return query_embedding.cpu().numpy()

    def search(self, query, top_n=3):
        keywords = self.extract_keywords(query)
        keyword_matches = self.keyword_search(keywords)

        if keyword_matches:
            print("Keyword-based matches found.")
            return [(rule_id, rule_text, 1.0) for rule_id, rule_text in keyword_matches][:top_n]
        else:
            print("Performing semantic search...")
            query_embedding = self.embed_query(query)
            similarities = cosine_similarity(query_embedding, self.rule_embeddings)[0]
            top_indices = np.argsort(similarities)[-top_n:][::-1]
            return [(self.rule_ids[i], self.rules_text[i], similarities[i]) for i in top_indices]

    def extract_keywords(self, query):
        query = query.lower()
        keywords = re.findall(r'\b[a-zA-Z]+\b', query)
        return [word for word in keywords if word not in EmbeddingConfig["stopwords"]]

    def keyword_search(self, keywords):
        matching_rules = []
        for idx, rule in enumerate(self.rules_text):
            for keyword in keywords:
                if keyword in rule.lower():
                    matching_rules.append((self.rule_ids[idx], rule))
                    break  # Avoid duplicate entries for the same rule
        return matching_rules

if __name__ == "__main__":
    searcher = SemanticSearcher()
    query = "What happens if a player shoots the puck out of the rink?"
    results = searcher.search(query)

    print("\nTop matching rules:")
    for rule_id, rule_text, similarity in results:
        print(f"Rule {rule_id} - Similarity: {similarity:.4f}")
