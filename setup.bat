@echo off
REM Complete Setup Script for IDEP (Windows)

echo 🚀 Setting up IDEP Application...

REM 1. Install Python dependencies
echo 📦 Installing Python packages...
pip install -r requirements.txt

REM 2. Setup database
echo 🗄️  Setting up database...
python setup_db.py

REM 3. Create required directories
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs

echo ✅ Setup complete!
echo.
echo 🔍 Running verification...
python verify_setup.py

echo.
echo To start the application:
echo   1. Make sure Ollama is running: ollama serve
echo   2. Pull a model: ollama pull llama3.2
echo   3. Start API: python run.py
echo   4. Start UI: streamlit run streamlit_app/app.py
echo.
echo API will be available at: http://localhost:8000
echo Docs will be available at: http://localhost:8000/docs
echo UI will be available at: http://localhost:8501
pause
