import unicodedata
import config

def normalize(text: str) -> str:
    """Türkçe karakterleri bozmadan stabilize eder (NFC)."""
    return unicodedata.normalize("NFC", text)

def chunk_text(text: str, max_len: int = config.CHUNK_SIZE) -> list[str]:
    text = normalize(text.replace("\n", " "))
    sentences = text.split(". ")
    chunks = []
    current = ""
    for sentence in sentences:
        if not sentence.strip():
            continue
        candidate = current + sentence + ". "
        if len(candidate) <= max_len:
            current = candidate
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence + ". "
    if current.strip():
        chunks.append(current.strip())
    return chunks
