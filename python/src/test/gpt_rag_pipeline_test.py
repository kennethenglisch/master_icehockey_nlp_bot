from rulebot.rag_pipeline import RagPipeline
from rulebot.config import ApiConfig
from rulebot.auth import get_api_key_local

if __name__ == "__main__":
    openai_api_key = get_api_key_local()
    pipeline = RagPipeline(
        openai_api_key=openai_api_key,
        embedder_model_name=ApiConfig["embedder_model_name"],
        embedding_dim=ApiConfig["embedding_dim"],
        top_k_chunks=ApiConfig["top_k_chunks"],
        top_k_rules=ApiConfig["top_k_rules"],
        top_k_situations=ApiConfig["top_k_situations"],
        threshold=ApiConfig["threshold"],
        situation_threshold=ApiConfig["situation_threshold"],
        model=ApiConfig["model"],
        temperature=ApiConfig["temperature"],
        max_length=ApiConfig["max_length"],
        index_path=ApiConfig["index_path"],
        mapping_path=ApiConfig["chunk_mapping_path"],
        casebook_index_path=ApiConfig["casebook_index_path"],
        casebook_mapping_path=ApiConfig["casebook_chunk_mapping_path"],
    )

    # Beispielabfrage
    # query = "The offending team is substituting and deliberately not playing the puck to avoid a penalty. Should icing be called?"
    # query = "Team A is on the power play. The puck is cleared down the ice and goes all the way to the Team A goalkeeper. There is no pressure being applied by Team B as they are in the process of a line change. The Team A goalkeeper covers the puck trying in an obvious attempt to get a stoppage of play. The Referee blows the whistle and proceeds to assess the goalkeeper a minor penalty for delay of game. The goalkeeper quickly explains to the Referee that the main problem was that a pad strap was untied and that the goalkeeper wanted to stop play to fix it. There is a huddle amongst the officials and they decide to take the penalty away, with the ensuing face-off in the Team A end zone and play resumes with Team A still on the power play. Was this the correct way to handle this situation?"
    # query += "Team A is on the power play. The puck is cleared down the ice and goes all the way to the Team A goalkeeper. There is no pressure being applied by Team B as they are in the process of a line change. The Team A goalkeeper covers the puck trying in an obvious attempt to get a stoppage of play. The Referee blows the whistle and proceeds to assess the goalkeeper a minor penalty for delay of game. The goalkeeper quickly explains to the Referee that the main problem was that a pad strap was untied and that the goalkeeper wanted to stop play to fix it. There is a huddle amongst the officials and they decide to take the penalty away, with the ensuing face-off in the Team A end zone and play resumes with Team A still on the power play. Was this the correct way to handle this situation?"

    # query = "Linienschiedsrichter Kenneth Englisch möchte wissen, was ein Icing ist. Was ist ein Icing?"
    query = "Which infractions result in a double minor penalty?"
    answer, prompt, all_rules, top_rules, situations = pipeline.process_query(query)

    print("\n----- PROMPT -----\n")
    print(prompt)
    print("\n----- GPT-ANSWER -----\n")
    print(answer)
    print("\n----- Retrieved Rules -----\n")
    for rule in top_rules:
        print(f"- {rule['rule_id']}: {rule['rule_title']} - {rule['subrule_title']}", f"Similarity: {rule['score_sum']}")
    print("\n----- Retrieved Situations -----\n")
    for situation in situations:
        print(f"- Situation {situation['situation_id']}: {situation['question']}", f"Similarity: {situation['similarity']}")
