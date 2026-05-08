"""
Quick API Test Script
Tests if the API is working correctly
"""
import requests
import sys

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        r = requests.get(f"{API_BASE}/api/v1/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_templates():
    """Test templates endpoint"""
    print("\n🔍 Testing templates endpoint...")
    try:
        r = requests.get(f"{API_BASE}/api/v1/templates", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Templates loaded: {len(data)} templates")
            for t in data:
                print(f"   - {t['display_name']} ({len(t['fields'])} fields)")
            return True
        else:
            print(f"❌ Templates failed: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_documents():
    """Test documents list endpoint"""
    print("\n🔍 Testing documents endpoint...")
    try:
        r = requests.get(f"{API_BASE}/api/v1/documents", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Documents endpoint working: {len(data)} documents")
            return True
        else:
            print(f"❌ Documents failed: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("IDEP API Test Suite")
    print("=" * 60)
    
    results = []
    results.append(("Health", test_health()))
    results.append(("Templates", test_templates()))
    results.append(("Documents", test_documents()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20s} {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the API server.")
        sys.exit(1)
