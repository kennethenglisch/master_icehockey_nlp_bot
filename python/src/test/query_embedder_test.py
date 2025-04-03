from rulebot.query_embedder import QueryEmbedder

if __name__ == "__main__":
    long_query = (
        "This is a very long query intended to test the chunking and embedding behavior. " * 50 +
        "The text is repetitive on purpose so that we exceed the token limit."
    )

    # long_query = "During the overtime, Team A is serving a minor penalty. The clock stops with 1:58 remaining in the period. Suddenly the Zamboni gate opens, and the ice crew comes onto the ice to shovel the excess snow. Is this permitted? Where do you find this in the rule book?"

    embedder = QueryEmbedder(
        tokenizer_name="sentence-transformers/all-MiniLM-L6-v2",
        embedder_model_name="sentence-transformers/all-MiniLM-L6-v2",
        overlap=1
    )

    # Generiere das Embedding
    embedding = embedder.embed_query(long_query)

    # Ausgabe
    print("Embedding shape:", embedding.shape)
    print("First 5 values of the embedding vector:", embedding[:5])
