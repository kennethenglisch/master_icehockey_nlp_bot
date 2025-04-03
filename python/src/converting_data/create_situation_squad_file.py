import json
import rulebot

class SituationsToSQuAD:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    def load_situations(self):
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File {self.input_file} not found.")
            return None
        except json.JSONDecodeError:
            print(f"Invalid JSON in {self.input_file}.")
            return None

    def convert_to_squad(self):
        situations_data = self.load_situations()
        if not situations_data:
            return

        squad_format = {
            "version": "v2.0",
            "data": []
        }

        for section in situations_data:
            section_name = section.get("section_name", "Unknown Section")
            section_number = section.get("section_number", "Unknown Number")

            for rule in section.get("section_rules", []):
                rule_number = rule.get("rule_number", "Unknown Rule")
                rule_title = f"{section_number} - Rule {rule_number}"

                paragraphs = []

                if rule.get("situations", None) is not None:
                    for situation in rule.get("situations", []):
                        context = situation.get("answer", "")
                        question = situation.get("question", "")
                        rule_references = situation.get("rule_reference", [])

                        if context and question:
                            qas = {
                                "question": question,
                                "id": situation['number'],
                                "answers": [
                                    {
                                        "text": context,
                                        "answer_start": 0
                                    }
                                ],
                                "metadata": {
                                    "rule_references": rule_references
                                },
                                "is_impossible": False
                            }

                            paragraphs.append({
                                "context": context,
                                "qas": [qas]
                            })

                    if paragraphs:
                        squad_format["data"].append({
                            "title": rule_title,
                            "paragraphs": paragraphs
                        })

            if section.get("section_situations", None) is not None:
                for situation in section.get("section_situations", []):
                    situation_number = situation.get("number", "Unknown Situation")
                    situation_title = f"{section_number} - Situation {situation_number}"

                    paragraphs = []

                    context = situation.get("answer", "")
                    question = situation.get("question", "")
                    rule_references = situation.get("rule_reference", [])

                    if context and question:
                        qas = {
                            "question": question,
                            "id": f"M-{situation['number']}",
                            "answers": [
                                {
                                    "text": context,
                                    "answer_start": 0
                                }
                            ],
                            "metadata": {
                                "rule_references": rule_references
                            },
                            "is_impossible": False
                        }

                        paragraphs.append({
                            "context": context,
                            "qas": [qas]
                        })

                    if paragraphs:
                        squad_format["data"].append({
                            "title": situation_title,
                            "paragraphs": paragraphs
                        })

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(squad_format, f, ensure_ascii=False, indent=4)

        print(f"SQuAD JSON file has been created.")

# Example usage
input_file = str(rulebot.data_dir) + '/json/situations/situations.json'
output_file = str(rulebot.data_dir) + '/json/squad/situations/squad_situations.json'

converter = SituationsToSQuAD(input_file, output_file)
converter.convert_to_squad()
