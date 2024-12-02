import openai
import json
import re
from datetime import datetime

openai.api_key = "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"

class CreateHockeyRuleQA:
    def __init__(self, rules_file, num_questions=5):
        print("Creating Hockey Rule SQuAD-File")
        self.rules_file = rules_file
        self.num_questions = num_questions
        self.start_time = datetime.now()
        self.rules_json = self.load_rules()

    def load_rules(self):
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"The file {self.rules_file} was not found.")
            return []
        except json.JSONDecodeError:
            print(f"The file {self.rules_file} contains invalid JSON.")
            return []

    def generate_questions_answers(self, section_name, rule_name, subrule_name, context, identifier):
        combined_context = (
            f"Section: {section_name}. Rule: {rule_name}. "
            f"Subrule: {subrule_name if subrule_name else 'N/A'}. "
            f"Details: {context}"
        )

        prompt = (
            f"Based on the following rule context, generate {self.num_questions} different questions that can be directly "
            f"and explicitly answered from the given context.\n\n"
            f"Context: {combined_context}\n\n"
            f"Ensure the questions are relevant, specific, and do not require external information or assumptions."
        )

        messages = [
            {"role": "system", "content": "You are an assistant that generates multiple context-specific questions based on hockey rules."},
            {"role": "user", "content": prompt}
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.0
            )
            generated_questions = response.choices[0].message["content"].strip().split("\n")

            qas = []
            for idx, question in enumerate(generated_questions):
                question = re.sub(r"^\s*\d+\.\s*", "", question).strip()
                if question:
                    qas.append({
                        "question": question,
                        "id": f"{identifier}-{idx + 1}",
                        "answers": [
                            {
                                "text": context,
                                "answer_start": 0
                            }
                        ]
                    })

            return qas
        except Exception as e:
            print(f"Error generating questions for {identifier}: {e}")
            return []

    def create_squad_format(self):
        squad_data = {
            "version": "v2.0",
            "data": []
        }

        total_items = sum(
            len(rule.get("subrules", [])) + 1  # +1 for the main rule
            for section in self.rules_json
            for rule in section.get("section_rules", [])
        )
        processed_items = 0

        for section in self.rules_json:
            section_name = section.get("section_name", "Unknown Section")
            for rule in section.get("section_rules", []):
                rule_name = rule.get("rule_name", "Unnamed Rule")
                paragraphs = []

                if rule.get("rule_text"):
                    rule_text = self.replace_placeholders(rule["rule_text"], rule.get("rule_reference", []))
                    qas = self.generate_questions_answers(
                        section_name,
                        rule_name,
                        None,  # No subrule name for main rule
                        rule_text,
                        f"{rule['rule_number']}"
                    )
                    if qas:
                        paragraphs.append({
                            "context": rule_text,
                            "qas": [qas]
                        })
                    processed_items += 1
                    self.display_progress(processed_items, total_items)

                for subrule in rule.get("subrules", []):
                    subrule_name = subrule.get("subrule_name", "Unnamed Subrule")
                    if subrule.get("rule_text"):
                        subrule_text = self.replace_placeholders(subrule["rule_text"], subrule.get("rule_reference", []))
                        qas = self.generate_questions_answers(
                            section_name,
                            rule_name,
                            subrule_name,
                            subrule_text,
                            subrule["subrule_number"]
                        )
                        if qas:
                            paragraphs.append({
                                "context": subrule_text,
                                "qas": [qas]
                            })
                        processed_items += 1
                        self.display_progress(processed_items, total_items)

                if paragraphs:
                    squad_data["data"].append({
                        "title": f"{section_name} - {rule_name}",
                        "paragraphs": paragraphs
                    })

        # show the completion of the process
        processed_items = total_items
        self.display_progress(processed_items, total_items)

        return squad_data

    def display_progress(self, processed, total):
        elapsed_time = datetime.now() - self.start_time
        elapsed_seconds = elapsed_time.total_seconds()

        avg_time_per_item = elapsed_seconds / processed if processed > 0 else 0
        remaining_items = total - processed
        remaining_time_seconds = avg_time_per_item * remaining_items

        hours = int(remaining_time_seconds // 3600)
        minutes = int((remaining_time_seconds % 3600) // 60)
        seconds = int(remaining_time_seconds % 60)

        remaining_time = f"{hours:02}:{minutes:02}:{seconds:02}"

        progress = (processed / total) * 100
        print(f"Progress: {progress:.2f}% ({processed}/{total} items processed) - Estimated remaining time: {remaining_time}", end="\r")

    def save_squad_file(self, output_file):
        squad_json = self.create_squad_format()
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(squad_json, f, ensure_ascii=False, indent=4)
        print(f"\nSQuAD JSON file has been created: {output_file}")

        end_time = datetime.now()
        elapsed_time = end_time - self.start_time
        print(f"Process completed in: {str(elapsed_time).split('.')[0]}")

    def replace_placeholders(self, text, rule_references):
        def replace_match(match):
            index = int(match.group(1))
            if index < len(rule_references):
                return "(" + rule_references[index] + ")"
            else:
                print(f"[Missing Reference {index}]")
                return f"[Missing Reference {index}]"

        return re.sub(r"{rule_reference_(\d+)}", replace_match, text)


# Example usage
#rules_file = "test.json" # for testing and saving credits on api (only a few rules)
rules_file = "rules.json"  # Path to the uploaded JSON file

current_timestamp = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
output_file = f"squad/hockey_rules_squad_format_{current_timestamp}.json"  # Output file name

hockey_bot = CreateHockeyRuleQA(rules_file, 5)
hockey_bot.save_squad_file(output_file)
