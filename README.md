# Yerel IaaS RAG Asistanı (Azure VM)

Bu proje, Azure VM (Standard_B4as_v2) üzerinde çalışan, internet bağlantısı gerektirmeyen, gizlilik odaklı bir RAG (Retrieval-Augmented Generation) sistemidir.

## 🚀 Özellikler
- **Modüler Mimari:** Temiz, bakımı kolay Python modülleri.
- **Tablo Ayıklama:** PDF içindeki tabloları satır bazlı analiz eder.
- **Batch Embedding:** Verileri 20'şerli gruplar halinde hızlıca vektörleştirir.
- **Hibrit Zeka:** Qwen tabanlı embedding ve chat modellerini kullanır.
- **Streamlit UI:** Kolay dosya yönetimi ve sohbet arayüzü.

## 🛠️ Kurulum

1. **Sanal Ortamı Hazırlayın:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Gerekli Paketleri Yükleyin:**
   ```bash
   pip install -r requirements.txt
   pip install pdfplumber
   ```

3. **Belgeleri Hazırlayın:**
   PDF ve TXT dosyalarınızı `sample_docs/` klasörüne koyun.

4. **Verileri Yükleyin:**
   ```bash
   python ingest_data.py
   ```

5. **Uygulamayı Çalıştırın:**
   ```bash
   streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
   ```

6. **Tarayıcıdan Açın:**
   Azure VM public IP adresiniz üzerinden `http://SUNUCU_IP:8501` adresine gidin.

## 📁 Proje Yapısı

- `config.py`: Model isimleri, chunk boyutları ve prompt ayarları.
- `db.py`: SQLite veritabanı işlemleri.
- `chunking.py`: Metin normalizasyonu ve chunk üretimi.
- `pdf_utils.py`: PDF metin ve tablo çıkarımı.
- `retrieval.py`: Embedding benzerlik araması.
- `ingest_data.py`: Belgeleri veritabanına yükleme scripti.
- `streamlit_app.py`: Web arayüzü ve soru-cevap akışı.
- `sample_docs/`: Kaynak PDF/TXT belgeler klasörü.

## ⚙️ Ayarlar
`config.py` dosyasında düzenlenebilir temel alanlar:

- `CHUNK_SIZE`: Metin parçalama uzunluğu.
- `TOP_K`: Sorgu başına getirilecek en alakalı chunk sayısı.
- `MIN_SIMILARITY`: Yetersiz eşleşmeleri elemek için benzerlik eşiği.
- `SYSTEM_PROMPT`: Modelin yalnızca belgeye dayalı cevap üretmesini sağlayan sistem promptu.

## ✅ Test Senaryoları

Örnek sorular:
- "Uç cihaz donanımı olarak ne kullanılmış ve özellikleri nelerdir?"
- "Sistemdeki orkestrasyon dili hangisidir?"
- "Google Coral TPU'nun enerji tüketimi nedir?"

## 📜 Not
Bu proje Azure VM üzerinde yerel RAG sistemini temiz ve modüler biçimde çalıştırmak amacıyla hazırlanmıştır.
