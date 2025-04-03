import torch
import json
import numpy as np
from transformers import AutoTokenizer, AutoModel
from typing_extensions import deprecated

from config import EmbeddingConfig

@deprecated
class Embedder:
    def __init__(self):
        print("Initializing Embedder")
        self.tokenizer = AutoTokenizer.from_pretrained(EmbeddingConfig["model_name"])
        self.model = AutoModel.from_pretrained(EmbeddingConfig["model_name"])
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    @staticmethod
    def load_rulebook(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            rules = [{"id": item["id"], "text": item["text"]} for item in data]
        return rules

    def generate_embeddings(self, texts):
        inputs = self.tokenizer(
            texts,
            padding=EmbeddingConfig["padding"],
            truncation=True,
            max_length=EmbeddingConfig["max_length"],
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            return outputs.last_hidden_state.mean(dim=1).cpu().numpy()

    @staticmethod
    def save_embeddings(embeddings, ids, file_path):
        np.savez(file_path, embeddings=embeddings, ids=ids)
        print(f"Embeddings saved to {file_path}")

    @staticmethod
    def load_embeddings(file_path):
        data = np.load(file_path + ".npz", allow_pickle=True)
        return data["embeddings"], data["ids"]

# from text_chunker import TextChunker
# from chunk_embedder import ChunkEmbedder
#
# if __name__ == "__main__":
#     from transformers import AutoTokenizer
#
#     rule_text = """
#     During each regular period of the games in an IIHF Championship there shall be a maximum of three (3) commercial breaks, each with a maximum duration of seventy (70) seconds but can be subject to change for specific events. Commercial breaks shall be taken at the first stoppage of play after the following times on the game clock as it counts down: (I) Break number 1: 14.00 (min.) (II) Break number 2: 10.00 (min.) (III) Break number 3: 06.00 (min.) Despite the above indicated time slots, commercial breaks shall not be taken if: a) A goal is scored; b) A penalty shot is called; c) One of the Teams is playing short-handed; d) A fight breaks out on ice; e) An icing infraction is called; and f) The net is dislodged accidentally by a defending player (incl. goalkeeper); and g) The puck is shot into the end zone from beyond the center red line and the goalkeeper freezes the puck resulting in a stoppage of play. Exceptions from point e-g above is when a penalty or penalties are assessed in the stoppage that affects the on-ice strength of either team. In the event that a commercial break is not taken during the time slot prescribed above, because of the exceptions above, the missed commercial opportunity shall be made up at the first stoppage of play in the next commercial break time slot. If there is another incident where the second commercial break is missed, this procedure shall continue to repeat itself until all commercial breaks are taken. However, there must always be at least 60 seconds between two commercial breaks. Any extra commercial break taken during a time slot shall follow the procedure described above and they shall be eliminated from the last remaining time slot of that period. They shall not be used to create extra commercial inventory for broadcasters. However, in such instances, the Commercial Coordinator will be instructed to turn on the light and signal the truck that an optional commercial opportunity is being taken. No commercial breaks shall be taken in the final thirty (30) seconds of the first and second periods, as well as during the final two (2) minutes of the third period. No commercial breaks shall be granted during overtime. The Teams shall comply with the following provisions during commercial breaks: a) Goalkeepers will be allowed to go to their respective players’ bench. b) Teams are allowed to change lines once the referee blows the whistle signaling the teams to return to the face-off with 20 seconds remaining in the commercial stoppage. c) These line changes will follow the same protocol as a normal line change during a stoppage of play.
#     """
#
#     tokenizer = AutoTokenizer.from_pretrained("roberta-base")
#     chunker = TextChunker(tokenizer, max_tokens=256, overlap=1)
#     chunks = chunker.chunk_text(rule_text)
#
#     print("Created Chunks:")
#     for idx, chunk in enumerate(chunks):
#         print(f"Chunk {idx + 1}:\n{chunk}\n")
#
#     embedder = ChunkEmbedder()
#     embeddings = embedder.embed_chunks(chunks)