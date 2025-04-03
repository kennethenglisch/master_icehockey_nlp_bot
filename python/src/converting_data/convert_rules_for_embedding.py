import json
import rulebot
import re

class ConvertRulesForEmbedding:
    def __init__(self, rules_file_path):
        self.rules_file_path = rules_file_path

    @staticmethod
    def replace_placeholders(text, rule_references):
        def replace_match(match):
            index = int(match.group(1))
            if index < len(rule_references):
                return "(" + rule_references[index] + ")"
            else:
                print(f"[Missing Reference {index}]", rule_references, text[:32])
                return f"[Missing Reference {index}]"

        return re.sub(r"{rule_reference_(\d+)}", replace_match, text)

    def convert_rules(self):
        with open(self.rules_file_path, 'r', encoding='utf-8') as file:
            rules_data = json.load(file)

        formatted_rules = []

        for section in rules_data:
            for rule in section.get("section_rules", []):
                rule_title = rule.get("rule_name")

                # Add the main rule text if available
                if rule.get("rule_text"):
                    rule_id = rule.get("rule_number")
                    formatted_rules.append({
                        "id": rule_id,
                        "rule_title": rule_title,
                        "subrule_title": None,
                        "text": self.replace_placeholders(rule['rule_text'], rule.get('rule_reference', []))
                    })

                # Process subrules
                for subrule in rule.get("subrules", []):
                    subrule_title = subrule.get("subrule_name")
                    subrule_id = subrule.get("subrule_number")
                    if subrule.get("rule_text"):
                        formatted_rules.append({
                            "id": subrule_id,
                            "rule_title": rule_title,
                            "subrule_title": subrule_title,
                            "text": self.replace_placeholders(subrule['rule_text'], subrule.get('rule_reference', []))
                        })

        return formatted_rules

if __name__ == "__main__":
    converter = ConvertRulesForEmbedding(str(rulebot.data_dir) + "/json/rules/rules.json")
    converted_rules = converter.convert_rules()

    with open(str(rulebot.data_dir) + "/json/rules/rules_for_embedding.json", 'w', encoding='utf-8') as f:
        json.dump(converted_rules, f, ensure_ascii=False, indent=4)

    print("--------------------------------------------------")
    print("Rules were extracted and saved for embedding.")
    print("Found {} rules." .format(len(converted_rules)))