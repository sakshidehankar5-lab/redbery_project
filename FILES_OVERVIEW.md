# 📁 IDEP Files Overview

## 📖 Documentation Files (पढ़ने के लिए)

| File | Purpose | When to Read |
|------|---------|--------------|
| **START_HERE.md** | शुरुआत करने के लिए | सबसे पहले यहाँ से शुरू करें |
| **QUICK_START.md** | Detailed Hindi/English guide | Step-by-step setup के लिए |
| **CHECKLIST.md** | Verification checklist | Setup verify करने के लिए |
| **README_SETUP.md** | Complete setup guide | Detailed instructions के लिए |
| **README.md** | Technical documentation | Architecture समझने के लिए |
| **FILES_OVERVIEW.md** | यह file - Files की list | Files समझने के लिए |

## 🚀 Setup Scripts (Setup के लिए)

### Windows
| File | Purpose | Command |
|------|---------|---------|
| **setup.bat** | Complete setup | `setup.bat` |
| **start_api.bat** | Start API server | `start_api.bat` |
| **start_ui.bat** | Start Streamlit UI | `start_ui.bat` |

### Linux/Mac
| File | Purpose | Command |
|------|---------|---------|
| **setup.sh** | Complete setup | `bash setup.sh` |

## 🐍 Python Scripts (Run करने के लिए)

| File | Purpose | Command |
|------|---------|---------|
| **run.py** | Start API server | `python run.py` |
| **setup_db.py** | Setup database | `python setup_db.py` |
| **test_api.py** | Test API endpoints | `python test_api.py` |
| **test_sample.py** | Create sample documents | `python test_sample.py` |

## ⚙️ Configuration Files

| File | Purpose | Edit? |
|------|---------|-------|
| **.env** | Main configuration | ✅ Yes - Update paths & settings |
| **.env.example** | Example config | ❌ No - Reference only |
| **requirements.txt** | Python dependencies | ❌ No - Auto-used by pip |
| **pytest.ini** | Test configuration | ❌ No - For testing |
| **alembic.ini** | Database migrations | ❌ No - Advanced use |

## 📂 Application Code (Main Application)

### app/ - Main Backend
```
app/
├── main.py                    # FastAPI application entry
├── api/                       # API routes & schemas
│   ├── routes/
│   │   └── documents.py      # Document endpoints
│   └── schemas.py            # Request/response models
├── core/                      # Core utilities
│   ├── config.py             # Configuration
│   ├── exceptions.py         # Custom exceptions
│   └── logging.py            # Logging setup
├── db/                        # Database layer
│   ├── database.py           # DB connection
│   ├── models/
│   │   └── models.py         # SQLAlchemy models
│   └── repositories/
│       └── repositories.py   # Data access layer
├── services/                  # Business logic
│   ├── document_service.py   # Main orchestrator
│   ├── ocr_service.py        # OCR processing
│   ├── llm_service.py        # LLM extraction
│   └── classifier_service.py # Document classification
└── extractors/                # Extraction templates
    └── templates/
        └── extraction_templates.py
```

### streamlit_app/ - Web UI
```
streamlit_app/
└── app.py                     # Streamlit web interface
```

### tests/ - Test Suite
```
tests/
├── unit/
│   └── test_services.py      # Unit tests
└── integration/
    └── test_api.py           # API integration tests
```

## 🗄️ Database & Migrations

| Folder/File | Purpose |
|-------------|---------|
| **alembic/** | Database migration scripts |
| **idep.db** | SQLite database (created after setup) |

## 📁 Runtime Folders (Auto-created)

| Folder | Purpose | Created When |
|--------|---------|--------------|
| **uploads/** | Uploaded documents | First upload |
| **logs/** | Application logs | App starts |
| **test_documents/** | Sample test files | Run test_sample.py |

## 🐳 Docker Files (Optional - For Deployment)

| File | Purpose |
|------|---------|
| **docker-compose.yml** | Multi-container setup |
| **Dockerfile.api** | API container |
| **Dockerfile.ui** | UI container |

## 📊 File Usage Flow

### First Time Setup:
```
1. Read: START_HERE.md
2. Run: setup.bat (Windows) or setup.sh (Linux/Mac)
3. Edit: .env (update Tesseract path if needed)
4. Run: python test_api.py (verify)
```

### Daily Usage:
```
Terminal 1: ollama serve
Terminal 2: python run.py
Terminal 3: streamlit run streamlit_app/app.py
```

### Testing:
```
python test_api.py        # Test API
python test_sample.py     # Create samples
pytest                    # Run full test suite
```

## 🎯 Quick Reference

### Must Read (शुरुआत में):
1. ✅ START_HERE.md
2. ✅ QUICK_START.md
3. ✅ CHECKLIST.md

### Must Run (Setup के लिए):
1. ✅ setup.bat / setup.sh
2. ✅ python test_api.py

### Must Edit (Configuration):
1. ✅ .env (Tesseract path)

### Don't Touch (जब तक जरूरत न हो):
- ❌ app/ folder files
- ❌ requirements.txt
- ❌ alembic/
- ❌ pytest.ini

## 📝 File Sizes (Approximate)

| Type | Count | Total Size |
|------|-------|------------|
| Documentation | 6 files | ~50 KB |
| Python Code | 20+ files | ~100 KB |
| Config Files | 5 files | ~5 KB |
| Scripts | 7 files | ~10 KB |
| **Total** | **~40 files** | **~165 KB** |

## 🔍 Finding Files

### By Purpose:

**Want to start?**
→ START_HERE.md

**Need setup help?**
→ QUICK_START.md, CHECKLIST.md

**Want to configure?**
→ .env

**Want to test?**
→ test_api.py, test_sample.py

**Want to understand code?**
→ README.md, app/ folder

**Want to customize?**
→ app/extractors/templates/extraction_templates.py

## 💡 Tips

1. **Always start with**: START_HERE.md
2. **Keep .env backed up**: Contains your configuration
3. **Check logs**: logs/idep.log for errors
4. **Use test scripts**: Before real documents
5. **Read CHECKLIST.md**: If something doesn't work

---

**Note**: यह overview है सभी files का। Setup के लिए START_HERE.md से शुरू करें।
