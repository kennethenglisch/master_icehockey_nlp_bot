from .rule_book_retriever import RuleBookRetriever

class PromptBuilder:
    def __init__(self, rulebook_retriever: RuleBookRetriever):
        """
        Initializes the PromptBuilder with access to the rule book retriever.

        :param rulebook_retriever: Instance of RuleBookRetriever to resolve rule references.
        """
        self._rule_book_retriever = rulebook_retriever

    def build_prompt(self, query_text: str, retrieved_top_rules: list, retrieved_situations: list):
        """
        Constructs a GPT prompt using the retrieved rules and situations.

        :param query_text: The user's question.
        :param retrieved_top_rules: List of top rules with the following keys:
            - "rule_id": Rule ID.
            - "score_sum": Sum of similarities of all associated chunks.
            - "score_count": Number of chunks associated with this rule.
            - "rule_title": Rule title.
            - "subrule_title": Subrule title.
            - "text": Full rule text.
        :param retrieved_situations: List of top situations.
        :return: A formatted prompt string.
        """
        prompt = f"USER_QUESTION: {query_text}\n\n"
        prompt += "CONTEXT (relevant rule- and/or casebook excerpts):\n"

        if len(retrieved_top_rules) > 0:
            prompt += "RULES:\n\n"

        for rule in retrieved_top_rules:
            rule_id = rule.get("rule_id")
            rule_title = rule.get("rule_title")
            subrule_title = rule.get("subrule_title")
            text = rule.get("text")

            # Check if it's a subrule (rule ID contains a dot)
            if "." in rule_id:
                rule_info = f"{rule_id}: {rule_title} - {subrule_title}" if subrule_title else f"{rule_id}: {rule_title}"
            else:
                rule_info = f"{rule_id}: {rule_title}"

            prompt += f"- {rule_info}\n  {text}\n"

        if len(retrieved_top_rules) > 0:
            prompt += "\n\n"

        if len(retrieved_situations) > 0:
            prompt += "CASEBOOK:\n\n"

        for situation in retrieved_situations:
            rule_id = situation.get("rule_id")
            situation_id = situation.get("situation_id")
            question = situation.get("question")
            answer = situation.get("answer")
            rule_reference = situation.get("rule_reference")

            if rule_reference is None:
                referenced_rules = "None"
            else:
                referenced_rules = ""
                for reference in rule_reference:
                    rule = self._rule_book_retriever.get_rule_by_id(reference)
                    if rule:
                        if rule['subrule_title'] and rule['subrule_title'] != rule['rule_title']:
                            referenced_rules += f"{rule['rule_id']}: {rule['rule_title']} - {rule['subrule_title']}, "
                        else:
                            referenced_rules += f"{rule['rule_id']}: {rule['rule_title']}, "
                    else:
                        referenced_rules += f"{reference}, "

            referenced_rules = referenced_rules.rstrip(", ")

            prompt += f"- RULE {rule_id} (Situation {situation_id}):\nSituation-Question: {question}\nSituation-Answer: {answer}\n(Referenced Rules: {referenced_rules})\n"

        if len(retrieved_top_rules) == 0 and len(retrieved_situations) == 0:
            prompt += "No context found.\n\n"

        prompt += "\nPlease answer the USER_QUESTION based on the context above."

        return prompt
