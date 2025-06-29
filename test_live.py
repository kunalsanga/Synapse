#!/usr/bin/env python3
"""
Live Test of LinkedIn Sourcing Agent
"""
import requests
import json

def test_live_candidate_search():
    """Test the live candidate search functionality"""
    print("🎯 Live Test: Finding Candidates for Full Stack Developer")
    print("=" * 60)
    
    # Test job description
    job_description = """
    Looking for a Full Stack Developer with expertise in JavaScript, React, Node.js, and MongoDB. 
    Must have 3+ years of experience building web applications and APIs. 
    Experience with cloud platforms like AWS or Azure is a plus.
    """
    
    payload = {
        "job_description": job_description,
        "max_candidates": 3
    }
    
    try:
        print("🔍 Searching for candidates...")
        response = requests.post("http://localhost:8000/match", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Success! Found {data['candidates_found']} candidates")
            print(f"📊 Job ID: {data['job_id']}")
            print("\n🏆 Top Candidates:")
            
            for i, candidate in enumerate(data['top_candidates'], 1):
                print(f"\n{i}. {candidate['name']}")
                print(f"   Score: {candidate['fit_score']}/10")
                print(f"   Headline: {candidate.get('headline', 'N/A')}")
                print(f"   Location: {candidate.get('location', 'N/A')}")
                print(f"   Skills: {', '.join(candidate.get('skills', [])[:3])}")
                print(f"   LinkedIn: {candidate['linkedin_url']}")
                
                # Show scoring breakdown
                print("   📈 Score Breakdown:")
                for category, score in candidate['score_breakdown'].items():
                    print(f"      {category.title()}: {score}/10")
                
                # Show outreach message
                print(f"   💬 Outreach Message:")
                print(f"      {candidate['outreach_message'][:200]}...")
                print("-" * 40)
            
            # Show search metadata
            metadata = data['search_metadata']
            print(f"\n📊 Search Statistics:")
            print(f"   Total Profiles Found: {metadata['total_profiles_found']}")
            print(f"   Enriched Candidates: {metadata['enriched_candidates']}")
            print(f"   AI Scoring Used: {metadata['ai_scoring_used']}")
            print(f"   Search Timestamp: {metadata['search_timestamp']}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_live_candidate_search() 