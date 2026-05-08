# 🚀 START HERE - IDEP Quick Setup

## आपका पूरा Running Application तैयार है!

यह एक **100% मुफ्त** AI-powered document extraction system है जो Indian documents (Aadhaar, DL, Passport, Invoice) से automatically data निकालता है।

---

## 📋 Setup करने के लिए (सिर्फ 3 Steps)

### Step 1️⃣: Prerequisites Install करें

#### A. Tesseract OCR (Free)
**Windows:**
- Download: https://github.com/UB-Mannheim/tesseract/wiki
- Install करें और path note करें

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-hin
```

#### B. Ollama (Free Local AI)
- Download: https://ollama.com/download
- Install करें
- Model download करें:
```bash
ollama pull llama3.2
```

### Step 2️⃣: Application Setup

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
bash setup.sh
```

### Step 3️⃣: Start करें

**3 Terminals खोलें:**

**Terminal 1 - Ollama:**
```bash
ollama serve
```

**Terminal 2 - API:**
```bash
python run.py
```

**Terminal 3 - UI:**
```bash
streamlit run streamlit_app/app.py
```

---

## 🎯 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Web UI** | http://localhost:8501 | Document upload interface |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **API** | http://localhost:8000 | REST API endpoint |

---

## ✅ Verify Installation

```bash
# Test API
python test_api.py

# Create sample documents
python test_sample.py
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **START_HERE.md** | यह file - Quick start guide |
| **QUICK_START.md** | Detailed Hindi/English guide |
| **README_SETUP.md** | Complete setup instructions |
| **CHECKLIST.md** | Step-by-step verification checklist |
| **README.md** | Technical documentation |

---

## 🎨 How to Use

### Option 1: Web UI (सबसे आसान)

1. Open: http://localhost:8501
2. Upload document (Aadhaar/DL/Passport/Invoice)
3. Click "Extract Data"
4. View extracted fields

### Option 2: API (cURL)

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@aadhaar.jpg" \
  -F "document_type=auto"
```

### Option 3: Python Code

```python
import requests

with open("aadhaar.jpg", "rb") as f:
    files = {"file": f}
    data = {"document_type": "auto"}
    response = requests.post(
        "http://localhost:8000/api/v1/documents/upload",
        files=files,
        data=data
    )
    print(response.json()["extracted_fields"])
```

---

## 🔧 Configuration

`.env` file में settings:

```env
# LLM - Free local AI
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2

# Database - Free file-based
DATABASE_URL=sqlite:///./idep.db

# OCR - Free open-source
OCR_ENGINE=tesseract
TESSERACT_CMD=/usr/bin/tesseract  # Windows: C:/Program Files/Tesseract-OCR/tesseract.exe
```

---

## 📊 Supported Documents

| Document Type | Auto-Detect | Fields Extracted |
|---------------|-------------|------------------|
| **Aadhaar Card** | ✅ Yes | Name, Number, DOB, Gender, Address |
| **Driving Licence** | ✅ Yes | DL No, Name, DOB, Vehicle Classes |
| **Passport** | ✅ Yes | Passport No, Name, Nationality, MRZ |
| **Invoice** | ✅ Yes | Invoice No, Vendor, Items, GST, Total |

---

## 🐛 Common Issues & Solutions

### ❌ Tesseract not found
```bash
# .env में सही path डालें
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe  # Windows
```

### ❌ Ollama connection error
```bash
# Check if running
ollama list

# Start Ollama
ollama serve

# Re-download model
ollama pull llama3.2
```

### ❌ Port already in use
```bash
# .env में port change करें
PORT=8001
```

### ❌ Database error
```bash
# Database recreate करें
rm idep.db  # Linux/Mac
del idep.db  # Windows
python setup_db.py
```

---

## 💡 Pro Tips

1. **Better Accuracy:**
   - High quality images use करें (300 DPI+)
   - Clear, well-lit photos
   - Document को flat रखें

2. **Faster Processing:**
   - Smaller model: `ollama pull phi3`
   - Image size reduce करें

3. **Hindi Support:**
   ```env
   OCR_LANGUAGE=eng+hin
   ```

4. **Different Models:**
   ```bash
   ollama pull llama3.2    # Best overall
   ollama pull mistral     # Fast
   ollama pull phi3        # Smallest
   ollama pull gemma2      # Google's
   ```

---

## 📁 Project Structure

```
idep/
├── app/                    # Main application code
├── streamlit_app/         # Web UI
├── test_documents/        # Sample test files
├── uploads/               # Uploaded documents
├── logs/                  # Application logs
├── .env                   # Configuration
├── setup.bat/sh          # Setup scripts
├── run.py                # API runner
└── START_HERE.md         # This file
```

---

## 🎓 Learning Path

1. ✅ **Setup** - Follow this guide
2. ✅ **Test** - Use sample documents
3. ✅ **Explore** - Try API docs
4. ✅ **Customize** - Modify templates
5. ✅ **Deploy** - Production setup

---

## 📞 Need Help?

1. **Check Logs:**
   ```bash
   # View logs
   cat logs/idep.log  # Linux/Mac
   type logs\idep.log  # Windows
   ```

2. **Test API:**
   ```bash
   python test_api.py
   ```

3. **Verify Setup:**
   - Follow [CHECKLIST.md](CHECKLIST.md)

4. **Read Docs:**
   - [QUICK_START.md](QUICK_START.md) - Detailed guide
   - [README_SETUP.md](README_SETUP.md) - Setup help
   - [README.md](README.md) - Technical docs

---

## 💰 Cost Breakdown

| Component | Free Option | Paid Option |
|-----------|-------------|-------------|
| **LLM** | Ollama (local) | OpenAI GPT-4 (~₹2/page) |
| **Database** | SQLite | PostgreSQL (cloud) |
| **OCR** | Tesseract | Cloud APIs |
| **Hosting** | Local | Cloud servers |
| **TOTAL** | **₹0** | ~₹5-10/page |

---

## 🎉 Success Indicators

✅ All 3 terminals running without errors
✅ http://localhost:8501 opens UI
✅ http://localhost:8000/docs shows API
✅ `python test_api.py` passes all tests
✅ Sample document extraction works

---

## 🚀 Next Steps

1. [ ] Upload your first real document
2. [ ] Try all 4 document types
3. [ ] Explore API documentation
4. [ ] Customize extraction templates
5. [ ] Share with your team

---

## 🌟 Features

- ✅ Auto document type detection
- ✅ Multi-language OCR (English + Hindi)
- ✅ 100% free local processing
- ✅ Beautiful web interface
- ✅ REST API with docs
- ✅ SQLite database (no server needed)
- ✅ Extensible template system
- ✅ Production-ready architecture

---

## 📝 Quick Commands Reference

```bash
# Setup
setup.bat              # Windows setup
bash setup.sh          # Linux/Mac setup

# Start services
ollama serve           # Start Ollama
python run.py          # Start API
streamlit run streamlit_app/app.py  # Start UI

# Testing
python test_api.py     # Test API
python test_sample.py  # Create samples

# Database
python setup_db.py     # Setup database
rm idep.db            # Reset database

# Logs
cat logs/idep.log     # View logs
```

---

**🎊 Congratulations! Aapka IDEP application ready hai!**

Ab koi bhi Indian document upload karke test kar sakte hain.

Happy Extracting! 🚀
