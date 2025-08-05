import tiktoken
from typing import List

def get_tokenizer(model="gpt-4o"):
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")

def dividir_en_chunks(texto: str, max_tokens: int = 3000, overlap: int = 200) -> List[str]:
    tokenizer = get_tokenizer("gpt-4o")
    tokens = tokenizer.encode(texto)
    total_tokens = len(tokens)

    chunks = []
    i = 0
    while i < total_tokens:
        sub_tokens = tokens[i:i + max_tokens]
        chunk_text = tokenizer.decode(sub_tokens)
        chunks.append(chunk_text.strip())
        i += max_tokens - overlap  

    return chunks



