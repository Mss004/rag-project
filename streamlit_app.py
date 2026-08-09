import os
import unicodedata

import streamlit as st

import config
import db
import chunking
import retrieval
from pdf_utils import extract_pdf_content
from foundry_local_sdk import FoundryLocalManager, Configuration

#  Sayfa Ayarları                                                               

st.set_page_config(page_title="RAG Asistanı", page_icon="🤖", layout="wide")
st.title("📚 Yerel RAG Asistanı")
st.caption("Azure VM üzerinde çalışır — internet bağlantısı gerekmez.")

#  Model Yükleme (bir kez yüklenir, önbellekte kalır)                          

@st.cache_resource(show_spinner="Modeller yükleniyor, lütfen bekleyin...")
def load_models():
    cfg = Configuration(app_name="rag-staj-projesi")
    manager = FoundryLocalManager(cfg)
    models = manager.catalog.list_models()

    embed_info = next(
        m for m in models
        if config.EMBEDDING_MODEL in str(m.id).lower()
    )
    embed_info.load()
    embed_client = embed_info.get_embedding_client()

    chat_info = next(
        m for m in models
        if config.CHAT_MODEL in str(m.id).lower()
    )
    chat_info.load()
    chat_client = chat_info.get_chat_client()

    return embed_client, chat_client


@st.cache_resource
def get_db_connection():
    return db.get_connection()


embed_client, chat_client = load_models()
conn = get_db_connection()

#  Yardımcı Fonksiyonlar                                                        

def ingest_uploaded_file(uploaded_file) -> int:
    """
    Streamlit üzerinden yüklenen dosyayı işler ve DB'ye ekler.
    Dönüş: eklenen chunk sayısı
    """
    filename = uploaded_file.name

    # Dosyayı sample_docs/ klasörüne kaydet
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    save_path = os.path.join(config.DOCS_DIR, filename)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Aynı dosya daha önce yüklendiyse temizle
    db.delete_source(conn, filename)

    # Chunk çıkar
    if filename.lower().endswith(".pdf"):
        text, table_chunks = extract_pdf_content(save_path)
        if not text.strip() and not table_chunks:
            st.warning(f"'{filename}' okunamadı. Taranmış (resim) PDF olabilir.")
            return 0
    else:
        raw = uploaded_file.getvalue().decode("utf-8")
        text = unicodedata.normalize("NFKD", raw)
        table_chunks = []

    text_chunks = chunking.chunk_text(text)
    all_chunks  = text_chunks + table_chunks

    if not all_chunks:
        st.warning(f"'{filename}' için chunk üretilemedi.")
        return 0

    # Batch embedding
    response   = embed_client.generate_embeddings(all_chunks)
    embeddings = [item.embedding for item in response.data]

    db.insert_chunks(conn, filename, all_chunks, embeddings)
    return len(all_chunks)


def answer_question(question: str) -> tuple[str, list[dict]]:
    """
    Soruyu embedding'e çevirir, ilgili chunk'ları getirir, LLM'e sorar.
    Dönüş: (cevap_metni, kullanılan_sonuçlar)
    """
    query_emb = embed_client.generate_embedding(question).data[0].embedding
    results   = retrieval.retrieve(query_emb, conn)

    # Eşik altında sonuç yoksa modeli hiç çağırma
    if not results:
        return "Bu bilgi elimdeki belgelerde bulunmuyor.", []

    context = retrieval.build_context(results)
    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT.format(context=context)},
        {"role": "user",   "content": question},
    ]

    response = chat_client.complete_chat(messages=messages)
    answer   = response.choices[0].message.content
    return answer, results

#  Sidebar — Belge Yönetimi                                                     

with st.sidebar:
    st.header("📁 Belge Yönetimi")

    # Yüklü belgeler
    sources = db.list_sources(conn)
    total   = db.count(conn)

    if sources:
        st.success(f"✅ {len(sources)} belge yüklü ({total} chunk)")
        with st.expander("Yüklü belgeler"):
            for s in sources:
                st.markdown(f"- `{s}`")
    else:
        st.warning("Henüz belge yüklenmedi.")

    st.divider()

    # Dosya yükleme
    st.subheader("Yeni Belge Ekle")
    uploaded = st.file_uploader(
        "PDF veya TXT seçin",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    if st.button("📥 Yükle ve İşle", disabled=not uploaded):
        for uf in uploaded:
            with st.spinner(f"'{uf.name}' işleniyor..."):
                n = ingest_uploaded_file(uf)
            if n > 0:
                st.success(f"✅ '{uf.name}' → {n} chunk eklendi.")
        st.rerun()

    st.divider()

    # Veritabanını temizle
    if st.button("🗑️ Tüm Veritabanını Temizle", type="secondary"):
        db.clear_all(conn)
        st.success("Veritabanı temizlendi.")
        st.rerun()

#  Ana Alan — Sohbet                                                            

if db.count(conn) == 0:
    st.info("👈 Başlamak için sol panelden bir belge yükleyin.")
    st.stop()

# Sohbet geçmişini başlat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Geçmiş mesajları göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📎 Kullanılan kaynaklar"):
                for r in msg["sources"]:
                    st.markdown(
                        f"**{r['source']}** — skor: `{r['score']:.3f}`\n\n"
                        f"> {r['text'][:200]}..."
                    )

# Yeni soru
if question := st.chat_input("Belgelerle ilgili bir soru sorun..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Yanıt oluşturuluyor..."):
            answer, sources = answer_question(question)

        st.markdown(answer)

        if sources:
            with st.expander("📎 Kullanılan kaynaklar"):
                for r in sources:
                    st.markdown(
                        f"**{r['source']}** — skor: `{r['score']:.3f}`\n\n"
                        f"> {r['text'][:200]}..."
                    )
            best_score = sources[0]["score"]
            st.caption(f"En iyi eşleşme: `{best_score:.3f}` — {len(sources)} chunk kullanıldı")

    st.session_state.messages.append({
        "role":    "assistant",
        "content": answer,
        "sources": sources,
    })
