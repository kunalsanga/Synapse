#!/usr/bin/env python3
"""
Debug script to check LinkedIn URLs
"""
import requests
import json

def debug_linkedin_urls():
    """Test the API and check LinkedIn URLs"""
    print("🔍 Debugging LinkedIn URLs")
    print("=" * 40)
    
    # Test job description
    job_description = "We are looking for a Senior Software Engineer with 5+ years of experience in Python, React, and AWS."
    
    payload = {
        "job_description": job_description,
        "max_candidates": 3
    }
    
    try:
        print("🔍 Searching for candidates...")
        response = requests.post("http://localhost:8000/match", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Found {data['candidates_found']} candidates")
            print("\n📋 LinkedIn URLs:")
            
            for i, candidate in enumerate(data['top_candidates'], 1):
                print(f"\n{i}. {candidate['name']}")
                print(f"   URL: {candidate['linkedin_url']}")
                print(f"   URL Type: {type(candidate['linkedin_url'])}")
                print(f"   URL Length: {len(candidate['linkedin_url'])}")
                
                # Test if URL is valid
                if candidate['linkedin_url'].startswith('http'):
                    print(f"   ✅ Valid URL format")
                else:
                    print(f"   ⚠️  URL might need https:// prefix")
                
                # Try to open URL
                url = candidate['linkedin_url']
                if not url.startswith('http'):
                    url = 'https://' + url
                print(f"   Final URL: {url}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_linkedin_urls() 