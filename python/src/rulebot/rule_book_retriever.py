import json

class RuleBookRetriever:
    def __init__(self, rulebook_path: str):
        """
        Initializes the retriever with the path to the rulebook JSON file and loads the rulebook.
        :param rulebook_path: Path to the JSON file (e.g., rules_for_embedding.json).
        """
        self.rulebook_path = rulebook_path
        self.rules = self._load_rules()

    def _load_rules(self):
        """Loads the rulebook from the JSON file."""
        with open(self.rulebook_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_rule_by_id(self, rule_id: str):
        """
        Retrieves the full rule text for a given rule ID.
        :param rule_id: The rule ID (e.g., "1.2." or "32.4.").
        :return: A dictionary containing the rule ID, title, subrule title (if any), and the full text.
        """
        rule_id = rule_id.rstrip(".") + "."  # Ensure the rule ID ends with a dot for consistent matching
        for rule in self.rules:
            if rule.get("id") == rule_id:
                return {
                    "rule_id": rule["id"],
                    "rule_title": rule.get("rule_title", None),
                    "subrule_title": rule.get("subrule_title", None),
                    "text": rule.get("text", None)
                }
        return None  # If the rule ID is not found
