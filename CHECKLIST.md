# ✅ IDEP Setup Checklist

## Pre-Installation

- [ ] Python 3.10+ installed
- [ ] pip working
- [ ] Internet connection available

## Step 1: Install Tesseract OCR

### Windows
- [ ] Downloaded from: https://github.com/UB-Mannheim/tesseract/wiki
- [ ] Installed successfully
- [ ] Note installation path (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`)

### Linux
```bash
- [ ] sudo apt-get install tesseract-ocr tesseract-ocr-hin
```

### Mac
```bash
- [ ] brew install tesseract tesseract-lang
```

## Step 2: Install Ollama

- [ ] Downloaded from: https://ollama.com/download
- [ ] Installed successfully
- [ ] Can run: `ollama --version`
- [ ] Downloaded model: `ollama pull llama3.2`
- [ ] Ollama is running: `ollama serve`

## Step 3: Setup Application

### Windows
- [ ] Ran: `setup.bat`
- [ ] No errors during pip install
- [ ] Database created successfully
- [ ] Folders created: `uploads/`, `logs/`

### Linux/Mac
- [ ] Ran: `bash setup.sh`
- [ ] No errors during pip install
- [ ] Database created successfully
- [ ] Folders created: `uploads/`, `logs/`

## Step 4: Configure Environment

- [ ] `.env` file exists
- [ ] Updated `TESSERACT_CMD` path (if Windows)
- [ ] `LLM_PROVIDER=ollama` is set
- [ ] `OLLAMA_MODEL=llama3.2` is set
- [ ] `DATABASE_URL=sqlite:///./idep.db` is set

## Step 5: Start Services

### Ollama
- [ ] Terminal 1: `ollama serve` is running
- [ ] No errors in Ollama output

### API
- [ ] Terminal 2: `python run.py` is running
- [ ] API started on http://localhost:8000
- [ ] No errors in startup logs

### UI (Optional)
- [ ] Terminal 3: `streamlit run streamlit_app/app.py` is running
- [ ] UI opened in browser at http://localhost:8501
- [ ] No errors in Streamlit output

## Step 6: Verify Installation

### API Tests
- [ ] Ran: `python test_api.py`
- [ ] Health check: ✅ PASS
- [ ] Templates: ✅ PASS
- [ ] Documents: ✅ PASS

### Browser Tests
- [ ] Opened: http://localhost:8000/docs
- [ ] API documentation loads
- [ ] Can see all endpoints

### UI Tests
- [ ] Opened: http://localhost:8501
- [ ] UI loads without errors
- [ ] Can see upload interface
- [ ] API Status shows: ✅ API Online

## Step 7: Test with Sample Document

- [ ] Created samples: `python test_sample.py`
- [ ] Sample files created in `test_documents/`
- [ ] Uploaded `sample_aadhaar.png` via UI
- [ ] Extraction completed successfully
- [ ] Fields extracted correctly
- [ ] No errors in logs

## Troubleshooting

### If Tesseract not found:
- [ ] Updated `.env` with correct `TESSERACT_CMD` path
- [ ] Restarted API server

### If Ollama connection error:
- [ ] Checked `ollama serve` is running
- [ ] Ran `ollama list` to verify model
- [ ] Re-pulled model: `ollama pull llama3.2`

### If Database error:
- [ ] Deleted `idep.db`
- [ ] Ran `python setup_db.py` again

### If Port already in use:
- [ ] Changed `PORT=8001` in `.env`
- [ ] Restarted API server

## Final Verification

- [ ] ✅ All services running
- [ ] ✅ API responding
- [ ] ✅ UI accessible
- [ ] ✅ Test document processed successfully
- [ ] ✅ No errors in logs

## 🎉 Success!

Your IDEP application is fully functional and ready to use!

## Next Steps

1. [ ] Test with real documents
2. [ ] Try different document types
3. [ ] Explore API documentation
4. [ ] Customize extraction templates
5. [ ] Deploy to production (optional)

## Support

If any step fails:
1. Check logs: `logs/idep.log`
2. Review error messages
3. Consult [QUICK_START.md](QUICK_START.md)
4. Check [README_SETUP.md](README_SETUP.md)

## System Information

- OS: _______________
- Python Version: _______________
- Tesseract Version: _______________
- Ollama Version: _______________
- Installation Date: _______________

---

**Note**: Keep this checklist for future reference and troubleshooting.
