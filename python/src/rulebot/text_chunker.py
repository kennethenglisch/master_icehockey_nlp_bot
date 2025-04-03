import spacy
from transformers import AutoTokenizer

class TextChunker:
    def __init__(self, tokenizer: AutoTokenizer, max_tokens: int = 256, overlap: int = 0):
        """
        :param tokenizer: A Hugging Face tokenizer.
        :param max_tokens: Maximum number of tokens per chunk.
        :param overlap: Number of overlapping sentences between consecutive chunks.
        """
        self.tokenizer = tokenizer
        self.max_tokens = max_tokens
        self.overlap = overlap
        self.nlp = spacy.load("en_core_web_sm")

    def chunk_text(self, text: str):
        """
        Splits the text into chunks based on sentence boundaries and token length.
        :param text: The full input text.
        :return: List of text chunks.
        """
        doc = self.nlp(text)
        # Create a list of sentences
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # Calculate how many tokens the current chunk would have with this sentence added
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            token_count = len(self.tokenizer.encode(test_chunk, add_special_tokens=False))

            if token_count <= self.max_tokens:
                current_chunk = test_chunk
            else:
                # If the current chunk, including this sentence, exceeds the chunk, save the previous chunk (without this sentence)
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # If overlap is desired, extract the last 'overlap' sentences from the current chunk
                    if self.overlap > 0:
                        current_chunk_sentences = current_chunk.split('. ')
                        overlap_sentences = ". ".join(current_chunk_sentences[-self.overlap:]) if len(
                            current_chunk_sentences) >= self.overlap else current_chunk
                    else:
                        overlap_sentences = ""
                    # Start the new chunk with the overlap sentences and the current sentence
                    current_chunk = (overlap_sentences + " " + sentence).strip()
                else:
                    # If a single sentence is longer than max_tokens, add it anyway as its own chunk
                    print("------------------------------------------")
                    print("Warning: The sentence is longer than max_tokens. This leads to a loss of information in embedding, as all tokens are truncated after max_tokens.")
                    print("Sentence:", sentence)
                    print("------------------------------------------")
                    chunks.append(sentence)
                    current_chunk = ""

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
