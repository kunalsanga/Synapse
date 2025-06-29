#!/usr/bin/env python3
"""
Test script for Synapse Hackathon functionality
Demonstrates the enhanced LinkedIn sourcing agent with the Windsurf job description
"""

import requests
import json
import time

def test_hackathon_endpoint():
    """Test the hackathon endpoint with the Windsurf job description"""
    
    # Windsurf job description from the hackathon
    job_description = """
    Software Engineer, ML Research at Windsurf (Codeium)
    
    Windsurf is a Forbes AI 50 company building AI-powered developer tools. We're looking for a Software Engineer to train LLMs for code generation.
    
    Requirements:
    - Experience with machine learning and LLM training
    - Strong programming skills in Python, PyTorch, TensorFlow
    - Experience with code generation models
    - Knowledge of software engineering best practices
    - Experience with large-scale data processing
    
    Location: Mountain View, CA
    Salary: $140-300k + equity
    """
    
    print("🚀 Testing Synapse Hackathon LinkedIn Sourcing Agent")
    print("=" * 60)
    print(f"Job Description: {job_description[:100]}...")
    print()
    
    # Test the hackathon endpoint
    url = "http://localhost:8000/api/hackathon"
    
    payload = {
        "job_description": job_description,
        "max_candidates": 10
    }
    
    try:
        print("📡 Sending request to hackathon endpoint...")
        start_time = time.time()
        
        response = requests.post(url, json=payload, timeout=60)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f} seconds")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Success! Found {data['candidates_found']} candidates")
            print(f"🆔 Job ID: {data['job_id']}")
            print(f"📅 Timestamp: {data['processing_timestamp']}")
            print(f"🎯 Scoring Method: {data['scoring_method']}")
            print()
            
            # Display top candidates
            print("🏆 Top Candidates:")
            print("-" * 60)
            
            for i, candidate in enumerate(data['top_candidates'][:5], 1):
                print(f"\n{i}. {candidate['name']}")
                print(f"   📍 Location: {candidate['location']}")
                print(f"   💼 Headline: {candidate['headline']}")
                print(f"   ⭐ Fit Score: {candidate['fit_score']}/10")
                print(f"   🔗 LinkedIn: {candidate['linkedin_url']}")
                
                # Show score breakdown
                breakdown = candidate['score_breakdown']
                print(f"   📊 Score Breakdown:")
                print(f"      - Education (20%): {breakdown.get('education', 0):.1f}/10")
                print(f"      - Trajectory (20%): {breakdown.get('trajectory', 0):.1f}/10")
                print(f"      - Company (15%): {breakdown.get('company', 0):.1f}/10")
                print(f"      - Skills (25%): {breakdown.get('skills', 0):.1f}/10")
                print(f"      - Location (10%): {breakdown.get('location', 0):.1f}/10")
                print(f"      - Tenure (10%): {breakdown.get('tenure', 0):.1f}/10")
                
                # Show skills
                if candidate['skills']:
                    print(f"   🛠️  Skills: {', '.join(candidate['skills'][:5])}")
                
                # Show companies
                if candidate['companies']:
                    print(f"   🏢 Companies: {', '.join(candidate['companies'][:3])}")
                
                # Show outreach message
                message = candidate['outreach_message']
                print(f"   💬 Outreach Message: {message[:150]}...")
            
            # Save results to file
            with open('hackathon_results.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Results saved to hackathon_results.json")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_web_interface():
    """Test the web interface"""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Web interface is accessible at http://localhost:8000")
        else:
            print(f"❌ Web interface error: {response.status_code}")
    except Exception as e:
        print(f"❌ Web interface error: {e}")

def test_api_docs():
    """Test the API documentation"""
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ API documentation is accessible at http://localhost:8000/docs")
        else:
            print(f"❌ API docs error: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs error: {e}")

if __name__ == "__main__":
    print("🧪 Synapse Hackathon Test Suite")
    print("=" * 60)
    
    # Test web interface
    test_web_interface()
    print()
    
    # Test API docs
    test_api_docs()
    print()
    
    # Test hackathon endpoint
    test_hackathon_endpoint()
    
    print("\n🎉 Test completed!")
    print("\n📋 Next steps:")
    print("1. Check hackathon_results.json for detailed results")
    print("2. Visit http://localhost:8000 for the web interface")
    print("3. Visit http://localhost:8000/docs for API documentation")
    print("4. Use the /api/hackathon endpoint for programmatic access") 