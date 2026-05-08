"""
Setup Verification Script
Checks if all prerequisites are installed correctly
"""
import sys
import subprocess
import os
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_python():
    """Check Python version"""
    print("\n🐍 Checking Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.10+")
        return False

def check_pip():
    """Check pip"""
    print("\n📦 Checking pip...")
    try:
        result = subprocess.run(["pip", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ pip installed - {result.stdout.strip()}")
            return True
        else:
            print("❌ pip not found")
            return False
    except Exception as e:
        print(f"❌ pip check failed: {e}")
        return False

def check_tesseract():
    """Check Tesseract OCR"""
    print("\n👁️  Checking Tesseract OCR...")
    
    # Try common paths
    paths = [
        "tesseract",
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
        "C:/Program Files/Tesseract-OCR/tesseract.exe",
        "C:/Program Files (x86)/Tesseract-OCR/tesseract.exe",
    ]
    
    for path in paths:
        try:
            result = subprocess.run([path, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                print(f"✅ Tesseract found at: {path}")
                print(f"   Version: {version}")
                return True, path
        except:
            continue
    
    print("❌ Tesseract not found")
    print("   Download: https://github.com/UB-Mannheim/tesseract/wiki")
    return False, None

def check_ollama():
    """Check Ollama"""
    print("\n🤖 Checking Ollama...")
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama installed - {result.stdout.strip()}")
            
            # Check if model is downloaded
            print("\n   Checking for llama3.2 model...")
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if "llama3.2" in result.stdout:
                print("   ✅ llama3.2 model found")
                return True
            else:
                print("   ⚠️  llama3.2 model not found")
                print("   Run: ollama pull llama3.2")
                return True  # Ollama is installed, just missing model
        else:
            print("❌ Ollama not found")
            return False
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        print("   Download: https://ollama.com/download")
        return False

def check_env_file():
    """Check .env file"""
    print("\n⚙️  Checking .env file...")
    if Path(".env").exists():
        print("✅ .env file exists")
        
        # Read and check key settings
        with open(".env", "r") as f:
            content = f.read()
            
        checks = {
            "LLM_PROVIDER": "ollama" in content,
            "DATABASE_URL": "sqlite" in content,
            "OCR_ENGINE": "tesseract" in content,
        }
        
        for key, found in checks.items():
            if found:
                print(f"   ✅ {key} configured")
            else:
                print(f"   ⚠️  {key} might need configuration")
        
        return True
    else:
        print("❌ .env file not found")
        print("   Copy from .env.example")
        return False

def check_folders():
    """Check required folders"""
    print("\n📁 Checking folders...")
    folders = ["uploads", "logs", "app", "streamlit_app"]
    all_ok = True
    
    for folder in folders:
        if Path(folder).exists():
            print(f"✅ {folder}/ exists")
        else:
            print(f"❌ {folder}/ missing")
            all_ok = False
    
    return all_ok

def check_database():
    """Check database"""
    print("\n🗄️  Checking database...")
    if Path("idep.db").exists():
        print("✅ Database file exists (idep.db)")
        return True
    else:
        print("⚠️  Database not created yet")
        print("   Run: python setup_db.py")
        return False

def check_dependencies():
    """Check Python dependencies"""
    print("\n📚 Checking Python dependencies...")
    
    required = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "pytesseract",
        "streamlit",
        "httpx",
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - missing")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def main():
    print_header("IDEP Setup Verification")
    
    results = {}
    
    # Run all checks
    results["Python"] = check_python()
    results["pip"] = check_pip()
    tesseract_ok, tesseract_path = check_tesseract()
    results["Tesseract"] = tesseract_ok
    results["Ollama"] = check_ollama()
    results["Environment"] = check_env_file()
    results["Folders"] = check_folders()
    results["Database"] = check_database()
    results["Dependencies"] = check_dependencies()
    
    # Summary
    print_header("Verification Summary")
    
    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {component:20s} {'PASS' if status else 'FAIL'}")
    
    # Overall status
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All checks passed! Your setup is complete.")
        print("\nNext steps:")
        print("  1. Start Ollama: ollama serve")
        print("  2. Start API: python run.py")
        print("  3. Start UI: streamlit run streamlit_app/app.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nRefer to:")
        print("  - START_HERE.md for setup guide")
        print("  - QUICK_START.md for detailed instructions")
        print("  - CHECKLIST.md for step-by-step verification")
    
    print("=" * 60)
    
    # Update .env with tesseract path if found
    if tesseract_ok and tesseract_path and Path(".env").exists():
        with open(".env", "r") as f:
            env_content = f.read()
        
        if "TESSERACT_CMD=" in env_content and tesseract_path not in env_content:
            print(f"\n💡 Tip: Update .env with:")
            print(f"   TESSERACT_CMD={tesseract_path}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
