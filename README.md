# 🤖 Local RAG Assistant

> A privacy-focused Retrieval-Augmented Generation (RAG) assistant for PDF and TXT documents. The system runs locally on an Azure Virtual Machine or a personal computer without sending documents to external services.

## 📌 Project Overview

This project is a local question-answering assistant based on the RAG architecture.

The system analyzes uploaded PDF and TXT documents, retrieves the most relevant text fragments for a user question, and generates an answer based only on the retrieved context.

Document processing, embedding generation, retrieval, and answer generation are performed locally through Microsoft Foundry Local. This helps protect document privacy and reduces unsupported answers based on information outside the uploaded sources.

## ✨ Key Features

- PDF and TXT document ingestion
- PDF text and table extraction with `pdfplumber`
- Semantic search using cosine similarity
- Local Qwen embedding and chat models
- SQLite-based data storage
- Streamlit-based web interface
- Source names and similarity scores in answers
- Real-time streamed responses
- Batch embedding for large documents
- Unicode NFC normalization for Turkish characters
- Top-3 retrieval for lower memory usage
- Strict context-only system prompt
- Similarity threshold to reduce unsupported answers
- Modular Python project structure
- Fully local processing through Microsoft Foundry Local

## 🛠️ Technology Stack

- Python
- Streamlit
- SQLite
- Microsoft Foundry Local
- Qwen3 Embedding 0.6B
- Qwen3.5 2B
- `pdfplumber`
- NumPy
- Azure Virtual Machine

## 🛠️ Installation — Azure Virtual Machine

### Requirements

- Azure VM: Standard_B4as_v2 or higher
- 4 vCPUs and 16 GB RAM recommended for the current configuration
- Ubuntu 22.04 LTS
- Python 3.10 or higher
- Microsoft Foundry Local
- At least 5 GB of available disk space

### Installation Steps

#### 1. Clone the repository

```bash
git clone https://github.com/Mss004/rag-project
cd rag-project
```

#### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install the required packages

```bash
pip install -r requirements.txt
```

#### 4. Download the Foundry Local models

The project uses the following models:

- Embedding model: `qwen3-embedding-0.6b-generic-cpu`
- Chat model: `qwen3.5-2b-generic-cpu`

If the Foundry CLI is available, run:

```bash
foundry model download qwen3-embedding-0.6b-generic-cpu
foundry model download qwen3.5-2b-generic-cpu
```

If you receive a `foundry: command not found` error, use the Foundry Local Python SDK:

```bash
python3 -c "
from foundry_local_sdk import FoundryLocalManager, Configuration

cfg = Configuration(app_name='rag-staj-projesi')
manager = FoundryLocalManager(cfg)

model = next(
    m for m in manager.catalog.list_models()
    if 'qwen3.5-2b-generic-cpu' in str(m.id)
)

model.download()
print('Chat model download completed.')
"
```

Make sure that the embedding model is also available in the local Foundry model catalog before starting the application.

#### 5. Add documents

You can copy PDF and TXT files into the `sample_docs/` directory:

```bash
cp /your/documents/*.pdf sample_docs/
cp /your/documents/*.txt sample_docs/
```

Alternatively, documents can be uploaded through the Streamlit interface.

#### 6. Create the database

```bash
python ingest_data.py
```

#### 7. Start the application

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

#### 8. Open the application

```text
http://[VM_PUBLIC_IP]:8501
```

> On Azure, allow inbound TCP traffic for port `8501` in the VM's Network Security Group.

## 💻 Installation — Personal Computer

### Requirements

| Requirement | Minimum | Recommended |
| --- | --- | --- |
| RAM | 8 GB | 16 GB |
| CPU | 4 cores | 8 cores |
| Storage | 5 GB free space | 10 GB free space |
| Python | 3.10+ | 3.12 |
| Foundry Local | Required | Latest available version |

### Installation Steps

#### 1. Clone the repository

```bash
git clone https://github.com/Mss004/rag-project
cd rag-project
```

#### 2. Create and activate a virtual environment

**Windows:**

```bash
python -m venv venv
venv\\Scripts\\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install the required packages

```bash
pip install -r requirements.txt
```

#### 4. Download the Foundry Local models

```bash
foundry model download qwen3-embedding-0.6b-generic-cpu
foundry model download qwen3.5-2b-generic-cpu
```

If the Foundry CLI is not available, use the Python SDK method described above.

#### 5. Add documents and create the database

Copy PDF or TXT documents into `sample_docs/`, or upload them through Streamlit. Then run:

```bash
python ingest_data.py
```

#### 6. Start the application

```bash
streamlit run streamlit_app.py
```

#### 7. Open the application

```text
http://localhost:8501
```

## 📁 Project Structure

```text
rag-project/
├── config.py           # Model and RAG configuration
├── db.py               # SQLite database operations
├── chunking.py         # Text normalization and chunking
├── pdf_utils.py        # PDF text and table extraction
├── retrieval.py        # Vector similarity search
├── ingest_data.py      # Document ingestion script
├── streamlit_app.py    # Streamlit web interface
├── test_rag.py         # Unit tests
├── requirements.txt    # Python dependencies
├── sample_docs/        # Sample documents directory
└── rag_database.db     # SQLite database created automatically
```

## ⚙️ Configuration

The main RAG settings can be changed in `config.py`.

| Parameter | Default Value | Description |
| --- | --- | --- |
| `CHUNK_SIZE` | `500` | Maximum text chunk size in characters |
| `TOP_K` | `3` | Number of the most relevant chunks retrieved for each query |
| `MIN_SIMILARITY` | `0.35` | Minimum similarity score required for retrieval |
| `EMBEDDING_MODEL` | `qwen3-embedding-0.6b` | Local embedding model |
| `CHAT_MODEL` | `qwen3.5-2b-generic-cpu` | Local chat model |

## 🔄 How the System Works

1. The user uploads a PDF or TXT document.
2. The document content is extracted.
3. PDF tables are processed together with the document text.
4. The text is normalized and divided into smaller chunks.
5. The chunks are converted into embeddings.
6. Embeddings and metadata are stored in SQLite.
7. The user asks a question through the Streamlit interface.
8. The question is converted into an embedding.
9. The most relevant chunks are retrieved using cosine similarity.
10. The retrieved context is sent to the local chat model.
11. The model generates an answer based only on the retrieved context.
12. The answer is displayed through a real-time streaming interface.

## 🧪 Example Questions

- What hardware was used for the edge device and what are its specifications?
- What is the orchestration language used in the system?
- How do TinyML and the SLM work together in this system?
- What are the main experimental findings?
- What performance results were obtained?

The answers depend on the content of the documents uploaded to the system.

## ✅ Automated Tests

Run the unit tests with:

```bash
python3 test_rag.py
```

The tests cover:

- **Chunking:** Checks whether text is divided into chunks correctly.
- **Database:** Checks SQLite connection and basic data operations.
- **Normalization:** Checks Unicode normalization and Turkish character handling.

Example successful output:

```text
Ran 3 tests in 0.014s
OK
```

