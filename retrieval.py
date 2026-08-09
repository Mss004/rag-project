import math
import config
import db


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot    = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def retrieve(query_embedding: list[float],
             conn,
             top_k: int = config.TOP_K,
             min_similarity: float = config.MIN_SIMILARITY) -> list[dict]:
    """
    Sorgu vektörüne en yakın chunk'ları döndürür.

    Dönüş: [{"score": float, "source": str, "text": str}, ...]
    - min_similarity eşiğinin altındaki sonuçlar elenir
    - Eşik sağlanmazsa boş liste döner → chat modeli hiç çağrılmaz
    """
    rows = db.fetch_all(conn)  # [(source_file, text_chunk, embedding), ...]

    scored = [
        {
            "score":  cosine_similarity(query_embedding, emb),
            "source": source,
            "text":   text,
        }
        for source, text, emb in rows
    ]

    scored.sort(key=lambda x: x["score"], reverse=True)

    top = scored[:top_k]
    filtered = [r for r in top if r["score"] >= min_similarity]

    return filtered


def build_context(results: list[dict]) -> str:
    """
    Retrieve sonuçlarından LLM'e verilecek bağlam metnini oluşturur.
    Her chunk kaynak dosya adıyla birlikte gösterilir.
    """
    return "\n\n".join(
        f"[Kaynak: {r['source']}]\n{r['text']}"
        for r in results
    )
