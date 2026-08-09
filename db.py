import json
import sqlite3
import config


def get_connection() -> sqlite3.Connection:
    """Veritabanı bağlantısı döndürür; tablo yoksa oluşturur."""
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file      TEXT    NOT NULL,
            text_chunk       TEXT    NOT NULL,
            embedding_vector TEXT    NOT NULL
        )
    """)
    conn.commit()
    return conn


def insert_chunks(conn: sqlite3.Connection, source_file: str,
                  chunks: list[str], embeddings: list[list[float]]) -> None:
    """Chunk ve vektör çiftlerini toplu olarak veritabanına yazar."""
    conn.executemany(
        "INSERT INTO documents (source_file, text_chunk, embedding_vector) "
        "VALUES (?, ?, ?)",
        [
            (source_file, chunk, json.dumps(embedding))
            for chunk, embedding in zip(chunks, embeddings)
        ]
    )
    conn.commit()


def delete_source(conn: sqlite3.Connection, source_file: str) -> None:
    """Belirli bir kaynak dosyaya ait tüm chunk'ları siler (yeniden yükleme için)."""
    conn.execute("DELETE FROM documents WHERE source_file = ?", (source_file,))
    conn.commit()


def clear_all(conn: sqlite3.Connection) -> None:
    """Tüm veritabanını siler — sıfırdan ingest için."""
    conn.execute("DELETE FROM documents")
    conn.commit()


def fetch_all(conn: sqlite3.Connection) -> list[tuple]:
    """(source_file, text_chunk, embedding) listesi döndürür."""
    rows = conn.execute(
        "SELECT source_file, text_chunk, embedding_vector FROM documents"
    ).fetchall()
    return [(r[0], r[1], json.loads(r[2])) for r in rows]


def count(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]


def list_sources(conn: sqlite3.Connection) -> list[str]:
    """Veritabanındaki kaynak dosya adlarını döndürür."""
    rows = conn.execute(
        "SELECT DISTINCT source_file FROM documents ORDER BY source_file"
    ).fetchall()
    return [r[0] for r in rows]
