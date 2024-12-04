import openai
import json
from datetime import datetime
from rulebot.auth import get_api_key

class SquadAnswerRefiner:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.start_time = datetime.now()
        openai.api_key = get_api_key()

    def load_squad_data(self):
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File {self.input_file} not found.")
            return None
        except json.JSONDecodeError:
            print(f"Invalid JSON in {self.input_file}.")
            return None

    def refine_answer(self, question, long_answer):
        prompt = (
            f"Based on the following hockey rule context, generate a precise and clear answer to the given question.\n\n"
            f"Question: {question}\n"
            f"Rule Context: {long_answer}\n\n"
            f"Ensure the answer is concise, accurate, and directly addresses the question, even if it requires interpretation or summarization."
        )

        messages = [
            {"role": "system", "content": "You are an assistant that refines answers to make them concise and relevant."},
            {"role": "user", "content": prompt}
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.0
            )
            return response.choices[0].message["content"].strip()
        except Exception as e:
            print(f"Error refining answer: {e}")
            return long_answer

    def refine_squad_data(self):
        squad_data = self.load_squad_data()
        if not squad_data:
            return

        total_items = sum(
            len(article.get("paragraphs", []))
            for article in squad_data.get("data", [])
        )
        processed_items = 0

        for data in squad_data.get("data", []):
            for paragraph in data.get("paragraphs", []):
                context = paragraph["context"]
                for qas_group in paragraph.get("qas", []):
                    # Iterate through the list of questions (qas)
                    for qa in qas_group:
                        question = qa["question"]
                        original_answer = qa["answers"][0]["text"]
                        refined_answer = self.refine_answer(question, original_answer)

                        # Update the answer in place
                        qa["answers"] = [
                            {
                                "text": refined_answer,
                                "answer_start": context.find(refined_answer) if refined_answer in context else 0
                            }
                        ]

                processed_items += 1
                self.display_progress(processed_items, total_items)

        self.save_squad_file(squad_data)

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

    def save_squad_file(self, squad_data):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(squad_data, f, ensure_ascii=False, indent=4)
        print(f"\nRefined SQuAD data saved to: {self.output_file}")

        end_time = datetime.now()
        elapsed_time = end_time - self.start_time
        print(f"Process completed in: {str(elapsed_time).split('.')[0]}")


input_file = "../../data/json/squad/hockey_rules_squad_format_2024-11-21_11.55.53.json"
#input_file = "squad/hockey_rules_squad_format_2024-11-20_16.06.23.json"

current_timestamp = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
output_file = f"data/json/squad/hockey_rules_squad_refined_{current_timestamp}.json"

refiner = SquadAnswerRefiner(input_file, output_file)
refiner.refine_squad_data()
