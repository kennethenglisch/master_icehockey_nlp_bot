from .config import EmbeddingConfig
from .query_embedder import QueryEmbedder
from .rule_book_retriever import RuleBookRetriever
from .faiss_index_manager import FaissIndexManager
from .retriever import Retriever
from .prompt_builder import PromptBuilder
from .answer_generator import AnswerGenerator

class RagPipeline:
    def __init__(self,
                 openai_api_key: str,
                 embedder_model_name: str,
                 embedding_dim: int,
                 top_k_chunks: int = 10,
                 top_k_rules: int = 3,
                 top_k_situations: int = 3,
                 threshold: float = 0.6,
                 situation_threshold: float = 0.6,
                 model: str = "gpt-4o-mini",
                 temperature: float = 0.0,
                 max_length: int = 4096,
                 index_path: str = EmbeddingConfig["index_output_path"],
                 mapping_path: str = EmbeddingConfig["chunk_mapping_path"],
                 casebook_index_path: str = EmbeddingConfig["casebook_index_output_path"],
                 casebook_mapping_path: str = EmbeddingConfig["casebook_chunk_mapping_path"],
                 ):
        """
        Initializes the RAG pipeline with retrieval, embedding, prompt building, and answer generation components.

        :param openai_api_key: API key for accessing the OpenAI GPT model.
        :param embedder_model_name: Name of the SentenceTransformer model used for embeddings (e.g., "sentence-transformers/all-MiniLM-L6-v2").
        :param embedding_dim: Dimensionality of the embedding vectors.
        :param top_k_chunks: Number of top rulebook chunks to retrieve for semantic similarity.
        :param top_k_rules: Number of top (complete) rules to use for the prompt.
        :param top_k_situations: Number of top similar casebook situations to retrieve.
        :param threshold: Similarity threshold for including rule chunks in the top results.
        :param situation_threshold: Similarity threshold for including situation handbook situations.
        :param model: Name of the GPT model used for answer generation (e.g., "gpt-4o", "gpt-4o-mini").
        :param temperature: Sampling temperature for the OpenAI model (higher values lead to more creative but potentially less accurate responses -> hallucination).
        :param max_length: Maximum number of tokens in the generated response.
        :param index_path: Path to the FAISS index for rulebook chunks.
        :param mapping_path: Path to the pickle file storing the mapping of rulebook chunks.
        :param casebook_index_path: Path to the FAISS index for situation handbook situations.
        :param casebook_mapping_path: Path to the pickle file storing the mapping of situation handbook situations.
        """
        self._openai_api_key = openai_api_key
        self._embedder_model_name = embedder_model_name
        self._embedding_dim = embedding_dim
        self._top_k_chunks = top_k_chunks
        self._top_k_rules = top_k_rules
        self._top_k_situations = top_k_situations
        self._threshold = threshold
        self._situation_threshold = situation_threshold
        self._model = model
        self._temperature = temperature
        self._max_length = max_length
        self._index_path = index_path
        self._mapping_path = mapping_path
        self._casebook_index_path = casebook_index_path
        self._casebook_mapping_path = casebook_mapping_path

        self._faiss_manager = FaissIndexManager(embedding_dim)
        self._faiss_manager.load_index(index_path)

        self._mapping_rulebook = Retriever.load_mapping(mapping_path)

        self._faiss_manager_casebook = FaissIndexManager(embedding_dim)
        self._faiss_manager_casebook.load_index(casebook_index_path)

        self._mapping_casebook = Retriever.load_mapping(casebook_mapping_path)

        self._query_embedder = QueryEmbedder(tokenizer_name=EmbeddingConfig["tokenizer_model_name"],
                                             embedder_model_name=self._embedder_model_name,
                                             overlap=EmbeddingConfig["overlap"])

        self._rulebook_retriever = RuleBookRetriever(EmbeddingConfig["rulebook_path"])
        self._prompt_builder = PromptBuilder(rulebook_retriever=self._rulebook_retriever)

    def process_query(self, query_text: str):
        """
        Executes the pipeline steps: retrieval, prompt creation, and generation.
        :param query_text: The user's question.
        :return: Tuple (generated_answer, prompt, retrieved_all_rules, retrieved_top_rules, retrieved_situations)
        """
        print("------ used configuration ------")
        print("Model:", self._model)
        print("Top k Chunks:", self._top_k_chunks)
        print("Top k Rules:", self._top_k_rules)
        print("Top k Situations:", self._top_k_situations)
        print("Threshold:", self._threshold)
        print("Situation Threshold:", self._situation_threshold)
        print("Temperature:", self._temperature)
        print("Max GPT Output-Length:", self._max_length)
        print("--------------------------------")

        query_embedding = self._query_embedder.embed_query(query_text)

        retriever = Retriever(
            embedding_dim=self._embedding_dim,
            top_k_chunks=self._top_k_chunks,
            top_k_rules=self._top_k_rules,
            top_k_situations=self._top_k_situations,
            threshold=self._threshold,
            situation_threshold=self._situation_threshold,
            rulebook_index=self._faiss_manager,
            casebook_index=self._faiss_manager_casebook,
            rulebook_mapping=self._mapping_rulebook,
            casebook_mapping=self._mapping_casebook,
            rulebook_retriever=self._rulebook_retriever
        )
        retrieved_chunks = retriever.retrieve_chunks(query_embedding)
        retrieved_all_rules, retrieved_top_rules = retriever.retrieve_rules_from_chunks(retrieved_chunks)
        retrieved_situations = retriever.retrieve_situations(query_embedding)

        prompt = self._prompt_builder.build_prompt(query_text, retrieved_top_rules, retrieved_situations)

        answer_generator = AnswerGenerator(
            openai_api_key=self._openai_api_key,
            model=self._model,
            temperature=self._temperature,
            max_length=self._max_length)
        response = answer_generator.generate_answer(prompt)

        if response["success"]:
            answer = response["answer"]

            if len(retrieved_top_rules) == 0 and len(retrieved_situations) == 0:
                answer += "\n\nPotentially relevant rules:\n"
                for rule in retrieved_all_rules:
                    rule_id = rule.get("rule_id")
                    rule_title = rule.get("rule_title")
                    subrule_title = rule.get("subrule_title")
                    rule_score = rule.get("score_sum")

                    # Check if it's a subrule (rule ID contains a dot)
                    if "." in rule_id:
                        rule_info = f"{rule_id}: {rule_title} - {subrule_title}" if subrule_title else f"{rule_id}: {rule_title}"
                    else:
                        rule_info = f"{rule_id}: {rule_title}"

                    answer += f"- {rule_info} (Score: {format(rule_score, '.4f')})\n"
        else:
            answer = "Fehler aufgetreten: " + response["answer"]

        return answer, prompt, retrieved_all_rules, retrieved_top_rules, retrieved_situations

# example queries
# "During the overtime, Team A is serving a minor penalty. The clock stops with 1:58 remaining in the period. Suddenly the Zamboni gate opens, and the ice crew comes onto the ice to shovel the excess snow. Is this permitted? Where do you find this in the rule book?"
# "Are commercial breaks allowed during overtime?"
# "Is it permitted to have commercial breaks during overtime in an IIHF Championship?"
# "The game clock shows that time has expired, but the horn has not sounded to signal the end of the period. Is the period over?"
# "Is a player off-side, when he enters the offending zone prior to the puck?"
# "If the defending team, while substituting player, doesn't play the icing puck to avoid a minor penalty for too many players on the ice, is this still considered icing?"
# "The attacking team is substituting and is not playing the puck to avoid a too many players penalty. Should icing be called?"
# "Linesperson Kenneth Englisch sees an too many men infraction and the team who should get a penalty is in control of the puck. What should he do in such situation?"
# "Linesperson Kenneth Englisch sees an too many men infraction and the team who should get a penalty is not in possession of the puck. What should he do in such situation?"
# "Team A makes a legal line change during the play. A17 comes on the ice and is away from the bench into the play. A21 is going off but not through the gate when the puck accidentally strikes A21. Is this a penalty? Where do you find this in the rule book?"
# "Player A12 gets a minor penalty for roughing and a minor penalty for slashing. Player B6 gets a minor penalty for roughing. What penalties should be shown on the game clock and at what strength will both teams play?"
# "Which penalty should be applied when a player looses his helmet on the ice?"
# "If a stick breaks, can the player still use it? What happens if he plays with it? What should the player do with a broken stick?"