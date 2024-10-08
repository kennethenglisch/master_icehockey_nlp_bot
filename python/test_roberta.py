import torch
from transformers import RobertaTokenizer, RobertaForMaskedLM

# Lade das vortrainierte RoBERTa-Modell und den Tokenizer
model_name = "roberta-large"
tokenizer = RobertaTokenizer.from_pretrained(model_name)
model = RobertaForMaskedLM.from_pretrained(model_name)

# Test-Text zum Verarbeiten
texts = [
    "Eishockey ist ein <mask> Sport.",
    "Der Spieler schießt den <mask>.",
    "Das Team gewinnt das <mask>."
]

for text in texts:
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = outputs.logits

    # Hole den Index des MASK-Token
    masked_index = torch.where(inputs["input_ids"][0] == tokenizer.mask_token_id)[0]

    if masked_index.numel() > 0:
        # Hole die Top-5 Vorhersagen für das MASK-Token
        predicted_indices = predictions[0, masked_index, :].topk(5).indices
        predicted_tokens = [tokenizer.decode(index) for index in predicted_indices]
        print(f"Text: {text} -> Top-5 Vorhersagen: {predicted_tokens}")
    else:
        print(f"Kein MASK-Token gefunden für den Text: '{text}'")
