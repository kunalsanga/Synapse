#!/usr/bin/env python3
"""
Quick test to verify the beautiful web interface is working
"""
import requests
import webbrowser
import time

def test_interface():
    """Test the beautiful web interface"""
    print("🌟 Testing Beautiful Web Interface")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Server is running and healthy")
        else:
            print("❌ Server health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Check if main page loads
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200 and "LinkedIn Sourcing Agent" in response.text:
            print("✅ Beautiful interface is loading correctly")
        else:
            print("❌ Interface not loading properly")
            return
    except Exception as e:
        print(f"❌ Cannot load interface: {e}")
        return
    
    # Test 3: Open browser
    print("🌐 Opening beautiful interface in browser...")
    webbrowser.open("http://localhost:8000")
    
    print("\n🎉 Interface Test Complete!")
    print("\n📋 What to do next:")
    print("1. The beautiful interface should have opened in your browser")
    print("2. You'll see a modern, professional design with tabs")
    print("3. Click 'Search Candidates' tab")
    print("4. Type a job description and click 'Find Candidates'")
    print("5. Watch the beautiful loading animation!")
    print("6. View results in the 'View Results' tab")
    
    print("\n🚀 Example job description to try:")
    print("We are looking for a Senior Software Engineer with 5+ years of experience in Python, React, and AWS. The role is based in San Francisco and involves building scalable web applications.")

if __name__ == "__main__":
    test_interface() 