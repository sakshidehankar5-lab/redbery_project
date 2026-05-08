# IDEP - Intelligent Document Extraction Platform

## 🚀 Quick Start (Free Setup)

### Prerequisites
- Python 3.10+
- Tesseract OCR
- Ollama (for free LLM)

### Installation Steps

#### 1. Install Tesseract OCR

**Windows:**
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-hin
```

**Mac:**
```bash
brew install tesseract tesseract-lang
```

#### 2. Install Ollama (Free Local LLM)

**Windows/Mac/Linux:**
```bash
# Visit: https://ollama.com/download
# Or on Linux:
curl -fsSL https://ollama.com/install.sh | sh
```

Pull a model:
```bash
ollama pull llama3.2
# Other free options: mistral, phi3, gemma2
```

#### 3. Setup Application

```bash
# Clone/navigate to project directory
cd idep

# Run setup script
bash setup.sh

# Or manually:
pip install -r requirements.txt
python setup_db.py
mkdir -p uploads logs
```

#### 4. Configure Environment

The `.env` file is already configured for free services:
- **LLM**: Ollama (local, free)
- **Database**: SQLite (file-based, no server)
- **OCR**: Tesseract (open-source)

No API keys needed!

#### 5. Start Application

**Terminal 1 - Start Ollama (if not running):**
```bash
ollama serve
```

**Terminal 2 - Start API:**
```bash
python run.py
# Or: uvicorn app.main:app --reload
```

**Terminal 3 - Start UI (optional):**
```bash
streamlit run streamlit_app/app.py
```

### Access Points

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501

## 📚 Supported Documents

1. **Aadhaar Card** - Indian national ID
2. **Driving Licence** - Indian DL
3. **Passport** - Indian passport
4. **Invoice** - GST invoices

## 🔧 Configuration

Edit `.env` file to customize:

```env
# Switch LLM models
OLLAMA_MODEL=llama3.2  # or mistral, phi3, gemma2

# Switch to PostgreSQL (optional)
DATABASE_URL=postgresql://user:pass@localhost:5432/idep_db

# OCR language
OCR_LANGUAGE=eng+hin  # English + Hindi
```

## 📖 API Usage

### Upload & Extract
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@aadhaar.jpg" \
  -F "document_type=auto"
```

### Get Templates
```bash
curl "http://localhost:8000/api/v1/templates"
```

### List Documents
```bash
curl "http://localhost:8000/api/v1/documents"
```

## 🐛 Troubleshooting

### Tesseract not found
```bash
# Update .env with correct path
TESSERACT_CMD=/usr/bin/tesseract  # Linux
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe  # Windows
```

### Ollama connection error
```bash
# Make sure Ollama is running
ollama serve

# Check if model is downloaded
ollama list
ollama pull llama3.2
```

### Database errors
```bash
# Recreate database
rm idep.db
python setup_db.py
```

## 💰 Cost Comparison

| Service | Free Option | Paid Option |
|---------|-------------|-------------|
| LLM | Ollama (local) | OpenAI GPT-4 ($0.03/1K tokens) |
| Database | SQLite | PostgreSQL (cloud hosting) |
| OCR | Tesseract | Cloud OCR APIs |

**Total Cost: ₹0 with free setup!**

## 🎯 Next Steps

1. Test with sample documents
2. Customize extraction templates in `app/extractors/templates/`
3. Add new document types
4. Deploy to production

## 📞 Support

For issues, check:
- API logs: `logs/idep.log`
- Ollama logs: `ollama logs`
- Database: `idep.db` (SQLite browser)
