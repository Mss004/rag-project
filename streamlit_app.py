import os
import time
import unicodedata
import streamlit as st
import config
import db
import chunking
import retrieval
from pdf_utils import extract_pdf_content
from foundry_local_sdk import FoundryLocalManager, Configuration


# ============================================================
# SAYFA AYARLARI
# ============================================================
st.set_page_config(page_title="Yerel RAG Asistanı", page_icon="🤖", layout="wide")
st.title("📚 Yerel RAG Asistanı")


# ============================================================
# MODEL YÜKLEME (Bir kez, önbellekte kalır)
# ============================================================
@st.cache_resource(show_spinner=False)
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


@st.cache_resource(show_spinner=False)
def get_db_connection():
    return db.get_connection()


# ============================================================
# SİSTEM BAŞLATMA DURUM MESAJLARI
# ============================================================
if "models_ready" not in st.session_state:
    with st.status("🧠 Sistem başlatılıyor...", expanded=True) as status:
        st.write("🔍 Modeller keşfediliyor...")
        embed_client, chat_client = load_models()
        st.write("✅ Embedding modeli hazır")
        st.write("✅ Chat modeli hazır")
        st.write("🗄️ Veritabanı bağlanıyor...")
        conn = get_db_connection()
        st.write("✅ Veritabanı hazır")
        status.update(label="🟢 Sistem hazır!", state="complete", expanded=False)
        st.session_state.models_ready = True
else:
    embed_client, chat_client = load_models()
    conn = get_db_connection()


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================
def ingest_uploaded_file(uploaded_file) -> int:
    """Streamlit üzerinden yüklenen dosyayı işler ve DB'ye ekler."""
    filename = uploaded_file.name
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    save_path = os.path.join(config.DOCS_DIR, filename)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    db.delete_source(conn, filename)

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
    all_chunks = text_chunks + table_chunks

    if not all_chunks:
        st.warning(f"'{filename}' için chunk üretilemedi.")
        return 0

    # BATCH İŞLEME: Embedding'leri 20'şerli gruplar halinde gönder
    # Ama progress bar 1'er 1'er artsın
    BATCH_SIZE = 20
    total = len(all_chunks)
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text(f"🔢 0/{total} chunk işleniyor...")

    for i in range(0, total, BATCH_SIZE):
        batch = all_chunks[i:i + BATCH_SIZE]
        response = embed_client.generate_embeddings(batch)
        embeddings = [item.embedding for item in response.data]
        db.insert_chunks(conn, filename, batch, embeddings)

        # Her chunk için progress bar'ı 1'er 1'er güncelle
        for j in range(len(batch)):
            current = i + j + 1
            progress_bar.progress(current / total)
            status_text.text(f"🔢 {current}/{total} chunk işleniyor...")

    return total


def answer_question_stream(question: str):
    """
    Soruyu alır, cevabı kelime kelime yield eder.
    Son dict içinde kaynaklar ve bitiş bayrağı döner.
    """
    # Kaynak arama sessizce yapılır, bildirim gösterilmez
    query_emb = embed_client.generate_embedding(question).data[0].embedding
    results = retrieval.retrieve(query_emb, conn)
    if not results:
        yield "Bu bilgi elimdeki belgelerde bulunmuyor."
        yield {"__done": True, "sources": []}
        return

    context = retrieval.build_context(results)
    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT.format(context=context)},
        {"role": "user", "content": question},
    ]

    response = chat_client.complete_chat(messages=messages)
    answer = response.choices[0].message.content

    # Streaming efekti: kelime kelime yield
    words = answer.split()
    for i, word in enumerate(words):
        if i < len(words) - 1:
            yield word + " "
        else:
            yield word
        time.sleep(0.03)

    # Son olarak kaynakları yield et
    yield {"__done": True, "sources": results}


# ============================================================
# SIDEBAR — BELGE YÖNETİMİ
# ============================================================
with st.sidebar:
    st.header("📁 Belge Yönetimi")
    sources = db.list_sources(conn)
    total = db.count(conn)

    if sources:
        st.success(f"✅ {len(sources)} belge yüklü ({total} chunk)")
        with st.expander("Yüklü belgeler"):
            for s in sources:
                st.markdown(f"- `{s}`")
    else:
        st.warning("Henüz belge yüklenmedi.")

    st.divider()

    st.subheader("Yeni Belge Ekle")
    uploaded = st.file_uploader(
        "PDF veya TXT seçin",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    if st.button("📥 Yükle ve İşle", disabled=not uploaded):
        for uf in uploaded:
            with st.status(f"'{uf.name}' işleniyor...", expanded=True) as status:
                st.write("💾 Dosya kaydediliyor...")
                st.write("📄 Metin çıkarılıyor...")
                n = ingest_uploaded_file(uf)
                if n > 0:
                    status.update(label=f"✅ '{uf.name}' → {n} chunk eklendi", state="complete")
                else:
                    status.update(label=f"⚠️ '{uf.name}' işlenemedi", state="error")
        st.rerun()

    st.divider()

    if st.button("🗑️ Tüm Veritabanını Temizle", type="secondary"):
        db.clear_all(conn)
        st.success("Veritabanı temizlendi.")
        st.rerun()


# ============================================================
# ANA ALAN — SOHBET
# ============================================================
if db.count(conn) == 0:
    st.info("👈 Başlamak için sol panelden bir belge yükleyin.")
    st.stop()

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

if question := st.chat_input("Belgelerle ilgili bir soru sorun..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        # Başlangıçta "Düşünüyor..." göster
        placeholder = st.empty()
        placeholder.markdown("🧠 Düşünüyor... ▌")
        full_answer = ""
        sources_data = []

        for token in answer_question_stream(question):
            if isinstance(token, dict) and token.get("__done"):
                sources_data = token.get("sources", [])
                break
            full_answer += token
            placeholder.markdown(full_answer + "▌")

        # Final metin (imleçsiz)
        placeholder.markdown(full_answer)

        if sources_data:
            with st.expander("📎 Kullanılan kaynaklar"):
                for r in sources_data:
                    st.markdown(
                        f"**{r['source']}** — skor: `{r['score']:.3f}`\n\n"
                        f"> {r['text'][:200]}..."
                    )
            best_score = sources_data[0]["score"]
            st.caption(f"En iyi eşleşme: `{best_score:.3f}` — {len(sources_data)} chunk kullanıldı")

        st.session_state.messages.append({
            "role": "assistant",
            "content": full_answer,
            "sources": sources_data,
        })
