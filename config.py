import os

# --- Dizinler & Dosyalar ---------------------------------------------------
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR    = os.path.join(BASE_DIR, "sample_docs")
DB_PATH     = os.path.join(BASE_DIR, "rag_database.db")

# --- Foundry Local Modelleri ----------------------------------------------
EMBEDDING_MODEL = "qwen3-embedding-0.6b-generic-cpu"
CHAT_MODEL      = "qwen2.5-7b-instruct-generic-cpu"

# --- RAG Davranışı --------------------------------------------------------
CHUNK_SIZE        = 500
TOP_K             = 6
MIN_SIMILARITY    = 0.35

# --- Sistem Promptu -------------------------------------------------------
SYSTEM_PROMPT = (
    "Sen bir dosya analiz asistanısın. Görevin SADECE verilen context (bağlam) metnine sadık kalarak cevap vermektir.\n"
    "KURALLAR:\n"
    "1. Eğer cevap context içinde doğrudan geçmiyorsa 'Bu bilgi belgelerde yok' de.\n"
    "2. Kendi dış bilgilerinden (Internet, otomotiv bilgisi vb.) ASLA ekleme yapma.\n"
    "3. Tablo verilerini görürsen (Anahtar: Değer formatında), bunları dikkatlice oku.\n"
    "4. Cevapların kısa, net ve sadece belgedeki kanıtlara dayalı olsun.\n\n"
    "Context:\n{context}"
)
