İşte README.md dosyasının tamamı, tek seferde kopyalayabilirsin:

```markdown
# 🤖 Yerel RAG Asistanı

> **İnternet bağlantısı gerektirmeyen**, gizlilik odaklı, Azure VM veya kişisel bilgisayar üzerinde çalışan yerel RAG (Retrieval-Augmented Generation) sistemi.

---

## 📌 Proje Hakkında

Bu sistem; PDF ve TXT belgelerini analiz ederek, kullanıcının sorularına yalnızca yüklenen belgelere dayanarak cevap üretir. Tüm işlemler **yerel olarak** gerçekleşir — hiçbir veri dışarıya gönderilmez.

### Temel Özellikler
- 📄 PDF ve TXT belgelerinden otomatik metin ve tablo çıkarımı
- 🔍 Vektör tabanlı anlamsal arama (Cosine Similarity)
- 🧠 Foundry Local üzerinde çalışan Qwen modelleri
- 🛡️ Hallucination önleme (benzerlik eşiği + sıkı sistem promptu)
- 🖥️ Streamlit tabanlı kullanıcı arayüzü
- ⚡ **Canlı Yanıt (Streaming):** Cevaplar gerçek zamanlı olarak kelime kelime yazılır.

---

## 🛠️ Kurulum — Seçenek 1: Azure VM 

### Gereksinimler
- Azure VM: Standard_B4as_v2 (4 vCPU, 16 GB RAM) veya üzeri
- Ubuntu 22.04 LTS
- Python 3.10+
- Foundry Local kurulu

### Adımlar

**1. Projeyi klonlayın:**
```bash
git clone https://github.com/Mss004/rag-project
cd rag-project
```

**2. Sanal ortam oluşturun:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Paketleri yükleyin:**
```bash
pip install -r requirements.txt
pip install pdfplumber
```

**4. Foundry Local modellerini indirin:**
```bash
foundry model download qwen3-embedding-0.6b-generic-cpu
foundry model download qwen2.5-7b-instruct-generic-cpu
```

**5. Belgelerinizi ekleyin:**
Terminal üzerinden:
```bash
cp /belgeleriniz/*.pdf sample_docs/
cp /belgeleriniz/*.txt sample_docs/
```
Veya `streamlit` üzerinden dosyalarınızı yükleyebilirsiniz.

**6. Veritabanını oluşturun:**
```bash
python ingest_data.py
```

**7. Uygulamayı başlatın:**
```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

**8. Tarayıcıdan açın:**
```text
http://[VM_PUBLIC_IP]:8501
```

---

## 💻 Kurulum — Seçenek 2: Kişisel Bilgisayar (Windows / macOS / Linux)

### Gereksinimler
| Gereksinim | Minimum | Önerilen |
|---|---|---|
| RAM | 8 GB | 16 GB |
| CPU | 4 Çekirdek | 8 Çekirdek |
| Depolama | 5 GB boş alan | 10 GB boş alan |
| Python | 3.10+ | 3.12 |
| Foundry Local | Kurulu olmalı | — |

### Foundry Local Kurulumu
Foundry Local'i kurmak için Microsoft'un resmi sayfasını ziyaret edin:  
👉 [Microsoft Foundry Local](https://github.com/microsoft/Foundry-Local)

### Adımlar

**1. Projeyi klonlayın:**
```bash
git clone https://github.com/Mss004/rag-project
cd rag-project
```

**2. Sanal ortam oluşturun:**

Windows:
```powershell
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Paketleri yükleyin:**
```bash
pip install -r requirements.txt
pip install pdfplumber
```

**4. Foundry Local modellerini indirin:**
```bash
foundry model download qwen3-embedding-0.6b-generic-cpu
foundry model download qwen2.5-7b-instruct-generic-cpu
```

**5. Belgelerinizi ekleyin:**
`sample_docs/` klasörüne PDF veya TXT dosyalarınızı kopyalayın veya `streamlit` üzerinden dosyalarınızı yükleyebilirsiniz.

**6. Veritabanını oluşturun:**
```bash
python ingest_data.py
```

**7. Uygulamayı başlatın:**
```bash
streamlit run streamlit_app.py
```

**8. Tarayıcıdan açın:**
```text
http://localhost:8501
```

---

## 📁 Proje Yapısı

```text
rag-project/
├── config.py           # Model ve RAG ayarları
├── db.py               # SQLite veritabanı işlemleri
├── chunking.py         # Metin normalizasyonu ve parçalama
├── pdf_utils.py        # PDF metin ve tablo çıkarımı
├── retrieval.py        # Vektör benzerlik araması
├── ingest_data.py      # Belge yükleme scripti
├── streamlit_app.py    # Web arayüzü
├── test_rag.py         # Otomatik birim testleri (Unit Tests)
├── requirements.txt    # Python bağımlılıkları
├── sample_docs/        # Kaynak belgeler klasörü
└── rag_database.db     # SQLite veritabanı (otomatik oluşur)
```

---

## ⚙️ Yapılandırma

`config.py` dosyasından aşağıdaki ayarları değiştirebilirsiniz:

| Parametre | Varsayılan | Açıklama |
|---|---|---|
| `CHUNK_SIZE` | 500 | Metin parçalama uzunluğu (karakter) |
| `TOP_K` | 6 | Sorgu başına getirilen chunk sayısı |
| `MIN_SIMILARITY` | 0.35 | Minimum benzerlik eşiği |
| `EMBEDDING_MODEL` | qwen3-embedding-0.6b | Embedding modeli |
| `CHAT_MODEL` | qwen2.5-7b-instruct | Sohbet modeli |

---

## 🧪 Test Soruları

Sistemi test etmek için örnek sorular:
- *"Uç cihaz donanımı olarak ne kullanılmış ve özellikleri nelerdir?"*
- *"Sistemdeki orkestrasyon dili hangisidir?"*
- *"TinyML ve SLM bu sistemde nasıl bir işbirliği yapıyor?"*

---

## ✅ Otomatik Testler

Projenin teknik doğruluğunu sağlamak için birim testleri (Unit Tests) eklenmiştir. Bu testler kodun temel fonksiyonlarını otomatik olarak denetler.

### Testleri Çalıştırma
```bash
python3 test_rag.py
```

### Test Kapsamı
- **Chunking:** Metinlerin doğru şekilde parçalara bölündüğünün kontrolü.
- **Database:** SQLite bağlantısı ve veri yazma/okuma testleri.
- **Normalization:** Türkçe karakterlerin (Unicode NFC/NFKD) doğru işlendiğinin kontrolü.

Başarılı test sonucu çıktısı:
```text
Ran 3 tests in 0.014s
OK
```

---

## 📜 Lisans
Bu proje staj eğitimi kapsamında geliştirilmiştir.
```
