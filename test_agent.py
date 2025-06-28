"""
Test script for the LinkedIn Sourcing Agent
"""
import requests
import json
import time

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_match_endpoint():
    """Test the main match endpoint"""
    job_description = """
    We are looking for a Senior Software Engineer with 5+ years of experience in Python, 
    React, and AWS. The role is based in San Francisco and involves building scalable 
    web applications. The ideal candidate should have experience with machine learning 
    and cloud infrastructure.
    """
    
    payload = {
        "job_description": job_description,
        "max_candidates": 5
    }
    
    try:
        print("🔍 Testing candidate search...")
        response = requests.post(
            "http://localhost:8000/match",
            json=payload,
            timeout=60  # Longer timeout for search
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Match endpoint test passed")
            print(f"Job ID: {result.get('job_id')}")
            print(f"Candidates found: {result.get('candidates_found')}")
            
            # Display top candidates
            candidates = result.get('top_candidates', [])
            for i, candidate in enumerate(candidates[:3], 1):
                print(f"\n--- Candidate {i} ---")
                print(f"Name: {candidate.get('name')}")
                print(f"Score: {candidate.get('fit_score')}")
                print(f"Headline: {candidate.get('headline')}")
                print(f"Location: {candidate.get('location')}")
                print(f"Skills: {candidate.get('skills', [])}")
                print(f"Message: {candidate.get('outreach_message', '')[:100]}...")
            
            return True
        else:
            print(f"❌ Match endpoint failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Match endpoint error: {e}")
        return False

def test_stats_endpoint():
    """Test the stats endpoint"""
    try:
        response = requests.get("http://localhost:8000/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Stats endpoint test passed")
            print(f"Total jobs processed: {stats.get('total_jobs_processed')}")
            print(f"OpenAI configured: {stats.get('openai_configured')}")
            return True
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting LinkedIn Sourcing Agent Tests")
    print("=" * 50)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    tests = [
        ("Health Check", test_health_check),
        ("Stats Endpoint", test_stats_endpoint),
        ("Match Endpoint", test_match_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The LinkedIn Sourcing Agent is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server logs for more details.")

if __name__ == "__main__":
    main() 