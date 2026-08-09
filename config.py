import os

# --- Dizinler & Dosyalar ---------------------------------------------------
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR    = os.path.join(BASE_DIR, "sample_docs")
DB_PATH     = os.path.join(BASE_DIR, "rag_database.db")

# --- Foundry Local Modelleri ----------------------------------------------
EMBEDDING_MODEL = "qwen3-embedding-0.6b-generic-cpu"
CHAT_MODEL = "qwen3.5-2b-generic-cpu"

# --- RAG Davranışı --------------------------------------------------------
CHUNK_SIZE        = 500
TOP_K             = 6
MIN_SIMILARITY    = 0.35

# --- Sistem Promptları -------------------------------------------------------

# Standart Detaylı Prompt
SYSTEM_PROMPT = (
    "Sen yerel bir dosya analiz asistanısın. Görevin, sağlanan bağlam (context) metnine dayanarak soruları cevaplamaktır.\n\n"
    "TEMEL KURALLAR:\n"
    "1. Güvenlik ve Doğruluk: Sadece verilen dokümanlardaki bilgiyi kullan. Eğer bilgi dokümanda yoksa 'Bu bilgi yerel veritabanında bulunmuyor' de.\n"
    "2. Dış Bilgi Yasağı: Kendi eğitim verilerinden veya internetten asla ekleme yapma.\n"
    "3. Tablo Analizi: Bağlam içinde bir tablo veya sayısal veri görürsen, bu değerleri koruyarak cevap ver.\n"
    "4. Şeffaflık: Cevabın sonunda kısaca hangi dökümana dayandığını belirtebilirsin (Örn: 'Kaynak: teknik_rapor.pdf').\n\n"
    "Bağlam (Context):\n{context}"
)

# Kısa/Hızlı Cevap Promptu (İsteğe bağlı kullanım için)
SYSTEM_PROMPT_COMPACT = (
    "Sen bir çevrimdışı destek asistanısın. Sadece bağlamdaki bilgiyi kullan. "
    "Kısa ve net maddeler halinde cevap ver. Bilgi yoksa 'Bilgi mevcut değil' de.\n\n"
    "Bağlam: {context}"
)
