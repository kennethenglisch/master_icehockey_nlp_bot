import torch
from transformers import pipeline, RobertaTokenizer, RobertaForMaskedLM

# Check if a GPU is available
device = 0 if torch.cuda.is_available() else -1  # Use GPU if available, otherwise use CPU

# Lade das RoBERTa-Modell
model_name = "roberta-large"
tokenizer = RobertaTokenizer.from_pretrained(model_name)
model = RobertaForMaskedLM.from_pretrained(model_name)

# Benutzeranfrage auf Deutsch
user_query_de = "Eishockey ist ein Sport."

# Übersetze die Anfrage ins Englische
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-de-en", device=device)  # Deutsch -> Englisch
user_query_en = translator(user_query_de)[0]['translation_text']

# Verarbeite die Anfrage mit dem RoBERTa-Modell
inputs = tokenizer(user_query_en, return_tensors="pt")
print("Tokenized Input IDs:", inputs["input_ids"])  # Print token IDs
print("Decoded Tokens:", tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]))  # Print decoded tokens

# Hole den Index des MASK-Token
print(user_query_de)
print(user_query_en)
