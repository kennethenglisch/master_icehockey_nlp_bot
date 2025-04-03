import json
import rulebot

class ConvertSituationsForEmbedding:
    def __init__(self, casebook_file_path):
        self.casebook_file_path = casebook_file_path

    def convert_situations(self):
        with open(self.casebook_file_path, 'r', encoding='utf-8') as file:
            casebook_data = json.load(file)

        formatted_situations = []

        # Durchlaufe alle Abschnitte im Casebook (Situationhandbook)
        for section in casebook_data:
            section_rules = section.get("section_rules", [])
            # Für jede Regel im Abschnitt:
            for rule in section_rules:
                # Nehme die Regelnummer und konvertiere sie ggf. in einen String
                rule_number = rule.get("rule_number")
                # Falls rule_number ein Integer ist, konvertiere ihn in String
                rule_id = str(rule_number) if rule_number is not None else "Unknown"

                situations = rule.get("situations")
                if situations:
                    for situation in situations:
                        formatted = {
                            "rule_id": rule_id,
                            "situation_id": situation.get("number", ""),
                            "question": situation.get("question", ""),
                            "answer": situation.get("answer", ""),
                            "rule_reference": situation.get("rule_reference", [])
                        }
                        formatted_situations.append(formatted)

        return formatted_situations

if __name__ == "__main__":
    converter = ConvertSituationsForEmbedding(str(rulebot.data_dir) + "/json/situations/situations.json")
    converted_situations = converter.convert_situations()

    with open(str(rulebot.data_dir) + "/json/situations/situations_for_embedding.json", 'w', encoding='utf-8') as f:
        json.dump(converted_situations, f, ensure_ascii=False, indent=4)

    print("--------------------------------------------------")
    print("Situations were extracted and saved for embedding.")
    print("Found {} situations." .format(len(converted_situations)))