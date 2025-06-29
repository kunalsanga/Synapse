#!/usr/bin/env python3
"""
LinkedIn Sourcing Agent - Feature Demonstration Script
This script demonstrates all the key features of the project.
"""

import requests
import json
import time
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']}")
            print(f"   Timestamp: {data['timestamp']}")
            print(f"   Gemini Available: {data['gemini_available']}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check Error: {e}")

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🏠 Testing Root Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root Endpoint: {data['message']}")
            print(f"   Version: {data['version']}")
            print("   Available Endpoints:")
            for endpoint, description in data['endpoints'].items():
                print(f"     {endpoint}: {description}")
        else:
            print(f"❌ Root Endpoint Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root Endpoint Error: {e}")

def test_candidate_matching():
    """Test the main candidate matching feature"""
    print("\n🎯 Testing Candidate Matching Feature...")
    
    # Example job descriptions to test
    job_descriptions = [
        {
            "title": "Senior Software Engineer",
            "description": "We are looking for a Senior Software Engineer with 5+ years of experience in Python, React, and AWS. The role is based in San Francisco and involves building scalable web applications. Must have experience with microservices architecture and cloud deployment.",
            "max_candidates": 5
        },
        {
            "title": "Data Scientist",
            "description": "Seeking a Data Scientist with expertise in machine learning, Python, and SQL. The role involves developing predictive models, analyzing large datasets, and working with stakeholders to drive business decisions. Experience with TensorFlow or PyTorch preferred.",
            "max_candidates": 3
        },
        {
            "title": "Product Manager",
            "description": "Looking for a Product Manager with 3+ years of experience in SaaS products. Must have strong analytical skills, experience with user research, and ability to work with engineering teams. Experience with agile methodologies and product analytics tools required.",
            "max_candidates": 4
        }
    ]
    
    for i, job in enumerate(job_descriptions, 1):
        print(f"\n📋 Testing Job {i}: {job['title']}")
        print(f"   Description: {job['description'][:100]}...")
        
        try:
            payload = {
                "job_description": job['description'],
                "max_candidates": job['max_candidates']
            }
            
            print("   🔍 Searching for candidates...")
            response = requests.post(f"{BASE_URL}/match", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Found {data['candidates_found']} candidates")
                print(f"   📊 Job ID: {data['job_id']}")
                
                # Show top candidate details
                if data['top_candidates']:
                    top_candidate = data['top_candidates'][0]
                    print(f"   🏆 Top Candidate: {top_candidate['name']}")
                    print(f"      Score: {top_candidate['fit_score']}/10")
                    print(f"      Headline: {top_candidate.get('headline', 'N/A')}")
                    print(f"      Location: {top_candidate.get('location', 'N/A')}")
                    print(f"      Skills: {', '.join(top_candidate.get('skills', [])[:3])}")
                    print(f"      Message Preview: {top_candidate['outreach_message'][:100]}...")
                
                # Show scoring breakdown
                if data['top_candidates']:
                    breakdown = data['top_candidates'][0]['score_breakdown']
                    print("   📈 Score Breakdown:")
                    for category, score in breakdown.items():
                        print(f"      {category.title()}: {score}/10")
                
                # Show search metadata
                metadata = data['search_metadata']
                print(f"   📊 Search Stats:")
                print(f"      Total Profiles Found: {metadata['total_profiles_found']}")
                print(f"      Enriched Candidates: {metadata['enriched_candidates']}")
                print(f"      AI Scoring Used: {metadata['ai_scoring_used']}")
                
                # Store job ID for later retrieval
                return data['job_id']
                
            else:
                print(f"   ❌ Matching Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Matching Error: {e}")
        
        # Add delay between requests
        time.sleep(2)
    
    return None

def test_results_retrieval(job_id):
    """Test retrieving results for a specific job"""
    if not job_id:
        print("\n❌ No job ID available for results retrieval test")
        return
    
    print(f"\n📋 Testing Results Retrieval for Job ID: {job_id}")
    try:
        response = requests.get(f"{BASE_URL}/results/{job_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Results Retrieved Successfully")
            print(f"   Job ID: {data['response']['job_id']}")
            print(f"   Candidates Found: {data['response']['candidates_found']}")
            print(f"   Timestamp: {data['timestamp']}")
        else:
            print(f"❌ Results Retrieval Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Results Retrieval Error: {e}")

def test_statistics():
    """Test the statistics endpoint"""
    print("\n📊 Testing Statistics Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Statistics Retrieved")
            print(f"   Total Jobs Processed: {data.get('total_jobs', 'N/A')}")
            print(f"   Total Candidates Found: {data.get('total_candidates', 'N/A')}")
            print(f"   Average Candidates per Job: {data.get('avg_candidates_per_job', 'N/A')}")
            print(f"   API Uptime: {data.get('uptime', 'N/A')}")
        else:
            print(f"❌ Statistics Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Statistics Error: {e}")

def demonstrate_features():
    """Main demonstration function"""
    print("🤖 LinkedIn Sourcing Agent - Feature Demonstration")
    print("=" * 60)
    print(f"🚀 Starting demonstration at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Base URL: {BASE_URL}")
    print("=" * 60)
    
    # Test all features
    test_health_check()
    test_root_endpoint()
    
    # Test the main feature - candidate matching
    job_id = test_candidate_matching()
    
    # Test additional features
    test_results_retrieval(job_id)
    test_statistics()
    
    print("\n" + "=" * 60)
    print("🎉 Feature Demonstration Complete!")
    print("\n📚 Key Features Demonstrated:")
    print("   ✅ Health Check & API Status")
    print("   ✅ Root Endpoint & API Information")
    print("   ✅ AI-Powered Candidate Matching")
    print("   ✅ Comprehensive Candidate Scoring")
    print("   ✅ Personalized Outreach Messages")
    print("   ✅ Results Retrieval & Storage")
    print("   ✅ Application Statistics")
    print("\n🔗 API Documentation: http://localhost:8000/docs")
    print("🌐 Interactive API: http://localhost:8000/")

if __name__ == "__main__":
    demonstrate_features() 