import os
import unicodedata

import config
import db
import chunking
from pdf_utils import extract_pdf_content
from foundry_local_sdk import FoundryLocalManager, Configuration



#  Model Yükleme                                                


def load_embedding_model():
    """Sadece embedding modelini yükler — chat modeli gerekmez."""
    cfg = Configuration(app_name="rag-staj-projesi")
    manager = FoundryLocalManager(cfg)
    models = manager.catalog.list_models()

    embed_info = next(
        m for m in models
        if config.EMBEDDING_MODEL in str(m.id).lower()
    )
    print(f"  Embedding modeli yükleniyor: {embed_info.id}")
    embed_info.load()
    return embed_info.get_embedding_client()


#  Dosya Okuma

def read_file(filepath: str) -> tuple[str, list[str]]:
    """
    PDF veya TXT dosyasını okur.
    Dönüş: (düz_metin, tablo_chunk_listesi)
    """
    if filepath.lower().endswith(".pdf"):
        text, table_chunks = extract_pdf_content(filepath)
        if not text.strip() and not table_chunks:
            print(f"  ⚠️  '{filepath}' okunamadı (taranmış PDF olabilir, OCR gerekir).")
        return text, table_chunks

    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()
    return unicodedata.normalize("NFKD", raw), []


#  Tek Dosya İşleme              

def ingest_file(filepath: str, embed_client, conn) -> int:
    """
    Bir dosyayı okur, chunk'lar, batch embedding alır ve DB'ye yazar.
    Dönüş: eklenen chunk sayısı
    """
    filename = os.path.basename(filepath)

    # Aynı dosya daha önce yüklendiyse temizle (yeniden yükleme desteği)
    db.delete_source(conn, filename)

    text, table_chunks = read_file(filepath)
    text_chunks = chunking.chunk_text(text)
    all_chunks = text_chunks + table_chunks

    if not all_chunks:
        print(f"  ⚠️  '{filename}' için chunk üretilemedi, atlanıyor.")
        return 0

    print(f"  📄 '{filename}' → {len(text_chunks)} metin + "
          f"{len(table_chunks)} tablo = {len(all_chunks)} chunk")

    # ✅ Mini-batch embedding — 20'şer chunk gönder (timeout önlemi)
    BATCH_SIZE = 20
    embeddings = []
    total_batches = (len(all_chunks) + BATCH_SIZE - 1) // BATCH_SIZE
    for b in range(total_batches):
        batch = all_chunks[b * BATCH_SIZE:(b + 1) * BATCH_SIZE]
        print(f"     Vektörleştiriliyor... batch {b+1}/{total_batches}", end="\r", flush=True)
        response = embed_client.generate_embeddings(batch)
        embeddings.extend([item.embedding for item in response.data])
    print(f"     Vektörleştiriliyor... ✓                    ")


    db.insert_chunks(conn, filename, all_chunks, embeddings)
    return len(all_chunks)


#  Ana Akış                                                                

def main():
    print("=" * 55)
    print("  RAG — Veri Yükleme (Ingestion)")
    print("=" * 55)

    # 1. Belge klasörünü kontrol et
    if not os.path.isdir(config.DOCS_DIR):
        os.makedirs(config.DOCS_DIR)
        print(f"\n'{config.DOCS_DIR}/' klasörü oluşturuldu.")
        print("İçine PDF veya TXT dosyası koy ve tekrar çalıştır.")
        return

    files = [
        f for f in os.listdir(config.DOCS_DIR)
        if f.lower().endswith((".pdf", ".txt"))
    ]

    if not files:
        print(f"\n⚠️  '{config.DOCS_DIR}/' içinde PDF veya TXT bulunamadı.")
        return

    print(f"\n{len(files)} dosya bulundu: {', '.join(files)}")

    # 2. Modeli yükle
    print("\n1. Embedding modeli başlatılıyor...")
    embed_client = load_embedding_model()

    # 3. Veritabanını hazırla
    print("\n2. Veritabanı hazırlanıyor...")
    conn = db.get_connection()

    # 4. Dosyaları işle
    print("\n3. Dosyalar işleniyor...")
    total_chunks = 0
    for filename in sorted(files):
        filepath = os.path.join(config.DOCS_DIR, filename)
        total_chunks += ingest_file(filepath, embed_client, conn)

    # 5. Sonuç
    conn.close()
    print(f"\n{'=' * 55}")
    print(f"  ✅ Tamamlandı! Toplam {total_chunks} chunk veritabanına eklendi.")
    print(f"  📂 Veritabanı: {config.DB_PATH}")
    print("=" * 55)


if __name__ == "__main__":
    main()
