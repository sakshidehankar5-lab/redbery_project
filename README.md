# 📄 IDEP — Intelligent Document Extraction Platform

AI-powered document data extraction platform supporting **Aadhaar Card**, **Driving Licence**, **Passport**, and **Invoice** documents — built with FastAPI, OCR, LLM, and Streamlit.

**🎉 100% FREE Setup Available** - Uses Ollama (local LLM), SQLite, and Tesseract OCR!

---

## 🚀 Quick Start (5 Minutes - Free Setup)

### Prerequisites
- Python 3.10+
- Tesseract OCR ([Download](https://github.com/UB-Mannheim/tesseract/wiki))
- Ollama ([Download](https://ollama.com/download))

### Installation

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
bash setup.sh
```

### Start Application

```bash
# 1. Start Ollama
ollama serve
ollama pull llama3.2

# 2. Start API
python run.py

# 3. Start UI (optional)
streamlit run streamlit_app/app.py
```

### Access
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs  
- **UI**: http://localhost:8501

📖 **Detailed Guide**: See [QUICK_START.md](QUICK_START.md) for Hindi/English instructions.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit UI  (:8501)                       │
│              File Upload + Extraction Preview                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP
┌───────────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend  (:8000)                     │
│   POST /documents/upload   GET /documents   GET /templates      │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │            DocumentProcessingService (Facade)           │    │
│  │  1. Validate & Save File                                │    │
│  │  2. OCRService (Tesseract / PaddleOCR)                  │    │
│  │  3. DocumentClassifier (Heuristics)                     │    │
│  │  4. LLMExtractionService (OpenAI / Anthropic / Azure)   │    │
│  │  5. Persist Results to PostgreSQL                       │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────────┘
                            │ SQLAlchemy
┌───────────────────────────▼─────────────────────────────────────┐
│                   PostgreSQL Database  (:5432)                  │
│   documents | ocr_results | extraction_results                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
idep/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   └── documents.py       # FastAPI route handlers
│   │   └── schemas.py             # Pydantic request/response models
│   ├── core/
│   │   ├── config.py              # pydantic-settings configuration
│   │   ├── exceptions.py          # Custom exception hierarchy
│   │   └── logging.py             # Aspect-based logging (loguru)
│   ├── db/
│   │   ├── models/models.py       # SQLAlchemy ORM models
│   │   ├── repositories/          # Repository pattern (data access layer)
│   │   └── database.py            # Async/sync session management
│   ├── extractors/
│   │   └── templates/
│   │       └── extraction_templates.py  # Template-based extraction config
│   ├── services/
│   │   ├── ocr_service.py         # OCR Strategy Pattern
│   │   ├── llm_service.py         # LLM Provider Strategy Pattern
│   │   ├── classifier_service.py  # Document type classifier
│   │   └── document_service.py    # Orchestrator / Facade
│   └── main.py                    # FastAPI app with middleware
├── streamlit_app/
│   └── app.py                     # Streamlit UI
├── tests/
│   ├── unit/test_services.py
│   └── integration/test_api.py
├── alembic/                       # DB migrations
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.ui
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start

### Option A — Docker Compose (Recommended)

```bash
# 1. Clone & enter
cd idep

# 2. Configure environment
cp .env.example .env
# Edit .env: add OPENAI_API_KEY or ANTHROPIC_API_KEY

# 3. Start everything
docker-compose up --build

# UI   → http://localhost:8501
# API  → http://localhost:8000/docs
```

### Option B — Local Development

```bash
# 1. Install system dependencies (Ubuntu/Debian)
sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin poppler-utils

# 2. Create virtual environment
python -m venv venv && source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Set up PostgreSQL
createdb idep_db
createuser idep_user
# grant privileges...

# 5. Configure
cp .env.example .env
# Edit DATABASE_URL, OPENAI_API_KEY, etc.

# 6. Run migrations
alembic upgrade head

# 7. Start API
uvicorn app.main:app --reload --port 8000

# 8. Start UI (new terminal)
streamlit run streamlit_app/app.py
```

---

## 🧩 Design Patterns Used

| Pattern | Where |
|---|---|
| **Strategy** | OCRService (Tesseract/PaddleOCR), LLMService (OpenAI/Anthropic/Azure) |
| **Factory Method** | `get_template()` — returns extraction template by document type |
| **Repository** | `DocumentRepository`, `OCRResultRepository`, `ExtractionResultRepository` |
| **Facade** | `DocumentProcessingService` — hides the full pipeline complexity |
| **Template Method** | `ExtractionTemplate` defines structure; LLM fills it |
| **Aspect (Decorator)** | `@log_execution`, `@log_exceptions` — cross-cutting logging |

---

## 🔧 Supported LLM Providers

Set `LLM_PROVIDER` in `.env`:

| Value | Description | Cost |
|---|---|---|
| `ollama` | Ollama (local) - **FREE** | Free |
| `openai` | OpenAI GPT-4o | ~₹2/page |
| `anthropic` | Anthropic Claude | ~₹2/page |
| `azure_openai` | Azure OpenAI | Varies |

**Recommended**: Use `ollama` with `llama3.2` for free local processing!

---

## 📋 Supported Document Types

| Type | Key Fields Extracted |
|---|---|
| `aadhaar` | Name, UID, DOB, Gender, Address |
| `driving_licence` | DL Number, Name, DOB, Expiry, Vehicle Classes |
| `passport` | Passport No, Name, Nationality, DOB, MRZ |
| `invoice` | Invoice No, GSTIN, Line Items, CGST/SGST/IGST, Total |

---

## 🧪 Running Tests

```bash
# Test API
python test_api.py

# Create sample documents
python test_sample.py

# Run pytest
pytest                          # all tests
pytest tests/unit/              # unit only
pytest tests/integration/       # integration only
pytest --cov=app --cov-report=html  # with coverage
```

---

## 📡 API Endpoints

| Method | URL | Description |
|---|---|---|
| `POST` | `/api/v1/documents/upload` | Upload & extract document |
| `GET` | `/api/v1/documents` | List all processed documents |
| `GET` | `/api/v1/documents/{id}` | Get extraction result by ID |
| `GET` | `/api/v1/templates` | List extraction templates |
| `GET` | `/api/v1/health` | Health check |

Interactive API docs: `http://localhost:8000/docs`
