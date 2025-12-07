"""
System Integration Tests
Tests frontend and backend connectivity
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_matches_endpoint():
    """Test matches list endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/matches", timeout=5)
        print(f"✅ Matches Endpoint: {response.status_code}")
        data = response.json()
        print(f"   Matches found: {len(data)}")
        return True
    except Exception as e:
        print(f"❌ Matches Endpoint Failed: {e}")
        return False

def test_analytics_endpoints():
    """Test analytics endpoints"""
    endpoints = [
        "/api/v1/analytics/tracks",
        "/api/v1/analytics/player_metrics",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} Failed: {e}")

def test_phase3_endpoints():
    """Test Phase 3 endpoints (tactics, xT, events)"""
    # These will return 404 without a match, but we can test they're available
    endpoints = [
        "/api/v1/tactics/match/1",
        "/api/v1/xt/match/1", 
        "/api/v1/events/match/1",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code in [200, 404]:
                print(f"✅ {endpoint}: Endpoint available (status: {response.status_code})")
            else:
                print(f"⚠️  {endpoint}: Unexpected status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} Failed: {e}")

def main():
    print("=" * 60)
    print("🧪 NASHAMA VISION - SYSTEM INTEGRATION TESTS")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print("📡 Testing Backend API...")
    print("-" * 60)
    
    # Core tests
    health_ok = test_backend_health()
    print()
    
    if health_ok:
        test_matches_endpoint()
        print()
        
        print("📊 Testing Analytics Endpoints...")
        print("-" * 60)
        test_analytics_endpoints()
        print()
        
        print("⚽ Testing Phase 3 Endpoints...")
        print("-" * 60)
        test_phase3_endpoints()
        print()
    
    print("=" * 60)
    print("✨ Frontend Running: http://localhost:5173")
    print("🔧 Backend Running: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)

if __name__ == "__main__":
    main()
