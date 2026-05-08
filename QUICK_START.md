# 🚀 IDEP - Quick Start Guide

## पूरी तरह से मुफ्त Setup (100% Free)

### Step 1: Prerequisites Install करें

#### A. Python (अगर नहीं है तो)
```bash
# Download from: https://www.python.org/downloads/
# Version 3.10 या उससे ऊपर
```

#### B. Tesseract OCR (Free)
**Windows:**
```bash
# Download करें: https://github.com/UB-Mannheim/tesseract/wiki
# Install करने के बाद path note करें (usually: C:\Program Files\Tesseract-OCR\tesseract.exe)
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-hin
```

#### C. Ollama (Free Local LLM)
**Windows/Mac/Linux:**
```bash
# Download: https://ollama.com/download
# Install करें और फिर model download करें:
ollama pull llama3.2
```

### Step 2: Application Setup

**Windows:**
```bash
# Setup script चलाएं
setup.bat
```

**Linux/Mac:**
```bash
# Setup script चलाएं
bash setup.sh
```

### Step 3: Configuration Check

`.env` file check करें:
```env
# LLM - Ollama (Free)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Database - SQLite (Free)
DATABASE_URL=sqlite:///./idep.db

# OCR - Tesseract (Free)
OCR_ENGINE=tesseract
TESSERACT_CMD=/usr/bin/tesseract  # Windows: C:/Program Files/Tesseract-OCR/tesseract.exe
```

### Step 4: Start करें

#### Terminal 1 - Ollama Start करें
```bash
ollama serve
```

#### Terminal 2 - API Start करें
**Windows:**
```bash
start_api.bat
```

**Linux/Mac:**
```bash
python run.py
```

#### Terminal 3 - UI Start करें (Optional)
**Windows:**
```bash
start_ui.bat
```

**Linux/Mac:**
```bash
streamlit run streamlit_app/app.py
```

### Step 5: Test करें

```bash
# API test करें
python test_api.py

# Browser में खोलें:
# API Docs: http://localhost:8000/docs
# UI: http://localhost:8501
```

## 📱 Usage Examples

### 1. Web UI से (सबसे आसान)
1. http://localhost:8501 खोलें
2. Document upload करें
3. "Extract Data" click करें
4. Results देखें

### 2. API से (cURL)
```bash
# Document upload करें
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@aadhaar.jpg" \
  -F "document_type=auto"

# Templates देखें
curl "http://localhost:8000/api/v1/templates"
```

### 3. Python से
```python
import requests

# Upload document
with open("aadhaar.jpg", "rb") as f:
    files = {"file": f}
    data = {"document_type": "auto"}
    response = requests.post(
        "http://localhost:8000/api/v1/documents/upload",
        files=files,
        data=data
    )
    result = response.json()
    print(result["extracted_fields"])
```

## 🎯 Supported Documents

| Document Type | Fields Extracted |
|---------------|------------------|
| **Aadhaar Card** | Name, Number, DOB, Gender, Address |
| **Driving Licence** | DL Number, Name, DOB, Address, Vehicle Classes |
| **Passport** | Passport No, Name, DOB, Nationality, MRZ |
| **Invoice** | Invoice No, Vendor, Customer, Items, GST, Total |

## 🔧 Troubleshooting

### Problem: Tesseract not found
**Solution:**
```bash
# .env में सही path डालें
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe  # Windows
TESSERACT_CMD=/usr/bin/tesseract  # Linux
```

### Problem: Ollama connection error
**Solution:**
```bash
# Check if Ollama is running
ollama list

# Start Ollama
ollama serve

# Pull model again
ollama pull llama3.2
```

### Problem: Database error
**Solution:**
```bash
# Database recreate करें
rm idep.db  # Linux/Mac
del idep.db  # Windows
python setup_db.py
```

### Problem: Port already in use
**Solution:**
```bash
# .env में port change करें
PORT=8001  # API के लिए
STREAMLIT_PORT=8502  # UI के लिए
```

## 💡 Tips

1. **Better Accuracy के लिए:**
   - High quality images use करें (300 DPI+)
   - Clear, well-lit photos लें
   - Document को flat रखें

2. **Faster Processing:**
   - Smaller models use करें: `ollama pull phi3`
   - Image size reduce करें (max 2MB)

3. **Hindi Support:**
   ```bash
   # .env में
   OCR_LANGUAGE=eng+hin
   ```

4. **Different LLM Models:**
   ```bash
   # Available free models:
   ollama pull llama3.2    # Best overall
   ollama pull mistral     # Fast
   ollama pull phi3        # Smallest
   ollama pull gemma2      # Google's model
   ```

## 📊 Performance

| Component | Time | Cost |
|-----------|------|------|
| OCR (Tesseract) | 1-3s per page | Free |
| LLM (Ollama) | 5-15s | Free |
| Total | 6-18s | Free |

## 🎓 Next Steps

1. ✅ Test with sample documents
2. ✅ Try different document types
3. ✅ Customize extraction templates
4. ✅ Add new document types
5. ✅ Deploy to production

## 📞 Need Help?

- Check logs: `logs/idep.log`
- API docs: http://localhost:8000/docs
- Test API: `python test_api.py`

## 🎉 Success!

Aapka IDEP application ab fully functional hai aur **100% free** hai!

Koi bhi document upload karke test kar sakte hain.
