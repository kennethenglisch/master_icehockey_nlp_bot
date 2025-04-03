import json
import rulebot

def validate_squad_format(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "data" not in data:
        return "Error: Missing 'data' key."
    for article in data["data"]:
        if "paragraphs" not in article:
            return f"Error: Missing 'paragraphs' in article: {article.get('title', 'unknown')}"
        for paragraph in article["paragraphs"]:
            if "context" not in paragraph:
                return "Error: Missing 'context' in paragraph."
            if "qas" not in paragraph:
                return "Error: Missing 'qas' in paragraph."
            for qa in paragraph["qas"]:
                if "question" not in qa:
                    return "Error: Missing 'question' in Q&A."
                if "answers" not in qa:
                    return "Error: Missing 'answers' in Q&A."
    return "SQuAD file structure is valid."

print(validate_squad_format(str(rulebot.data_dir) + "/json/squad/situations/squad_situations.json"))
print(validate_squad_format(str(rulebot.data_dir) + "/json/squad/situations/training_squad.json"))