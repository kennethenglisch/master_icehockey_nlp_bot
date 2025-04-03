from . import data_dir

ApiConfig = {
    "embedder_model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "embedding_dim": 384,#768,
    "top_k_chunks": 10,
    "top_k_rules": 3,
    "top_k_situations": 2,
    "threshold": 0.6,
    "situation_threshold": 0.8,
    "model": "gpt-4o-mini",
    "temperature": 0.0,
    "max_length": 4096,
    "index_path": str(data_dir) + "/roberta/embeddings/rulebook_faiss_index.index",
    "chunk_mapping_path": str(data_dir) + "/roberta/embeddings/rulebook_chunk_mapping.pkl",
    "casebook_index_path": str(data_dir) + "/roberta/embeddings/casebook_faiss_index.index",
    "casebook_chunk_mapping_path": str(data_dir) + "/roberta/embeddings/casebook_chunk_mapping.pkl",
    "rulebook_path": str(data_dir) + "/json/rules/rules_for_embedding.json",
}

EmbeddingConfig = {
    "tokenizer_model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "embedder_model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "rulebook_path": str(data_dir) + "/json/rules/rules_for_embedding.json",
    "index_output_path": str(data_dir) + "/roberta/embeddings/rulebook_faiss_index.index",
    "chunk_mapping_path": str(data_dir) + "/roberta/embeddings/rulebook_chunk_mapping.pkl",
    "casebook_path": str(data_dir) + "/json/situations/situations_for_embedding.json",
    "casebook_index_output_path": str(data_dir) + "/roberta/embeddings/casebook_faiss_index.index",
    "casebook_chunk_mapping_path": str(data_dir) + "/roberta/embeddings/casebook_chunk_mapping.pkl",
    "max_tokens": 256,
    "overlap": 1,
    "embedding_dim": 384, # see: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
}