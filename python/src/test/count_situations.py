import json
from pathlib import Path
import faiss
from sentence_transformers import SentenceTransformer

_package_dir = Path(__file__).resolve().parent
app_dir = _package_dir.parent.parent
config_dir = app_dir / "config"
data_dir = app_dir / "data"

with open(str(data_dir) + "/json/situations/situations_for_embedding.json", 'r', encoding='utf-8') as f:
    print("Situationen:", len(json.load(f)))

index = faiss.read_index(str(data_dir) + "/roberta/embeddings/rulebook_faiss_index.index")
situ_index = faiss.read_index(str(data_dir) + "/roberta/embeddings/casebook_faiss_index.index")

print("Anzahl Vektoren im Regelbuch-Index:", index.ntotal)
print("Anzahl Vektoren im Situations-Index:", situ_index.ntotal)

# model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
# print(model.get_max_seq_length())