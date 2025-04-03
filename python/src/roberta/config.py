from .. import rulebot

FirstTrainingConfig = {
    "model_name": "roberta-base",  # Pretrained model name
    "train_file": str(rulebot.data_dir) + "/json/squad/situations/squad_situations.json",  # Path to SQuAD training dataset
    #"train_file": str(rulebot.data_dir) + "/json/squad/situations/training_squad.json",  # Path to SQuAD training dataset
    "output_dir": str(rulebot.data_dir) + "/roberta/roberta_model_trained",  # Directory to save model
    "train_batch_size": 8,
    "eval_batch_size": 8,
    "learning_rate": 3e-5,
    "num_train_epochs": 6,
    "max_seq_length": 512,
    "warmup_steps": 0,
    "weight_decay": 0.01,
    "evaluation_strategy": "epoch",  # Evaluate at the end of each epoch
    "save_strategy": "epoch",  # Save the model at the end of each epoch
    "logging_dir": str(rulebot.data_dir) + "/roberta/logs",  # Directory for logging
    "logging_steps": 100,  # Log after every x steps
}

FineTuningConfig = {
    "model_name": str(rulebot.data_dir) + "/roberta/roberta_model_trained_v2",  # Pretrained model name
    "train_file": str(rulebot.data_dir) + "/json/squad/situations/squad_situations.json",  # Path to SQuAD training dataset
    #"train_file": str(rulebot.data_dir) + "/json/squad/situations/training_squad.json",  # Path to SQuAD training dataset
    # "train_file": str(rulebot.data_dir) + "/json/squad/situations/split_squad",  # Path to SQuAD training dataset
    "output_dir": str(rulebot.data_dir) + "/roberta/roberta_model_trained_v3",  # Directory to save model
    "train_batch_size": 16,
    "eval_batch_size": 16,
    "learning_rate": 2e-5,
    "num_train_epochs": 3,
    "max_seq_length": 512,
    "warmup_steps": 200,
    "weight_decay": 0.01,
    "evaluation_strategy": "epoch",  # Evaluate at the end of each epoch
    "save_strategy": "epoch",  # Save the model at the end of each epoch
    "logging_dir": str(rulebot.data_dir) + "/roberta/logs/training_v2",  # Directory for logging
    "logging_steps": 50,  # Log after every x steps
    "gradient_accumulation_steps": 2,  # Akkumulation für größere Batch-Sizes
    "fp16": True,  # Mixed Precision Training für schnellere Berechnungen,
    "lr_scheduler_type": "cosine_with_restarts",
    "max_grad_norm": 0.5,
    "early_stopping_patience": 2,
}

EvaluationConfig = {
    "model_path": str(rulebot.data_dir) + "/roberta/roberta_model_trained_v3",  # Path to the trained model
    "eval_file": str(rulebot.data_dir) + "/json/squad/situations/training_squad.json",  # Path to the evaluation dataset
    "max_seq_length": 512,  # Max sequence length for tokenization
}

STOPWORDS = [
    "the", "a", "an", "in", "on", "at", "is", "are", "was", "were", "be", "have", "has", "had",
    "do", "does", "did", "with", "for", "about", "between", "this", "that", "these", "those",
    "of", "to", "from", "and", "or", "by", "as", "if", "it", "its", "which", "what", "when",
    "where", "who", "whom", "why", "how", "all", "any", "each", "few", "more", "most", "some",
    "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "can", "will", "just", "should", "now", "then", "but", "because", "while", "before",
    "after", "above", "below", "up", "down", "out", "over", "under", "again", "further",
    "once", "here", "there", "etc", "i.e", "e.g", "rule", "rules", "section", "article",
    "paragraph", "subparagraph", "clause", "shall", "must", "may", "might", "could", "would"
]

EmbeddingConfig = {
    "tokenizer_model_name": "roberta-base",  # Path to the trained model
    "embedder_model_name": "sentence-transformers/all-MiniLM-L6-v2",#"sentence-transformers/all-mpnet-base-v2",
    "rulebook_path": str(rulebot.data_dir) + "/json/rules/rules_for_embedding.json",
    "index_output_path": str(rulebot.data_dir) + "/roberta/embeddings/rulebook_faiss_index.index",
    "chunk_mapping_path": str(rulebot.data_dir) + "/roberta/embeddings/rulebook_chunk_mapping.pkl",
    "casebook_path": str(rulebot.data_dir) + "/json/situations/situations_for_embedding.json",
    "casebook_index_output_path": str(rulebot.data_dir) + "/roberta/embeddings/casebook_faiss_index.index",
    "casebook_chunk_mapping_path": str(rulebot.data_dir) + "/roberta/embeddings/casebook_chunk_mapping.pkl",
    "max_tokens": 256,
    "overlap": 1,
    "embedding_dim": 384, # see: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
    "max_length": 4096,
    "temperature": 0.0,
    "model": "gpt-4o-mini",
}


