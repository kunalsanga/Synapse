#!/usr/bin/env python3
"""
Test Real LinkedIn Profiles
"""

import os
import sys
import json
from pathlib import Path

# Set up environment
os.environ["GEMINI_API_KEY"] = "AIzaSyA_rF9TDZruVbZC-XtQS71LAfphQLE6i7o"
os.environ["AI_PROVIDER"] = "gemini"
os.environ["DEBUG"] = "true"

def test_enhanced_search():
    """Test the enhanced search with real profiles"""
    print("🔍 Testing Enhanced Search with Real Profiles")
    print("=" * 60)
    
    try:
        # Import the enhanced search
        sys.path.append('agent')
        from enhanced_search import EnhancedLinkedInSearcher
        
        # Create searcher
        searcher = EnhancedLinkedInSearcher()
        
        # Test job description
        job_description = "Python React developer with AWS experience"
        
        print(f"🔍 Searching for: {job_description}")
        print()
        
        # Search for profiles
        profiles = searcher.search_linkedin_profiles(job_description, max_results=10)
        
        if profiles:
            print(f"✅ Found {len(profiles)} profiles")
            print()
            
            real_count = 0
            demo_count = 0
            
            for i, profile in enumerate(profiles, 1):
                url = profile.get('linkedin_url', '')
                name = profile.get('name', 'Unknown')
                headline = profile.get('headline', 'N/A')
                
                # Check if it's a real profile
                is_real = not any(demo_suffix in url for demo_suffix in ['-ai', '-dev', '-eng', '-aws', '-ml'])
                
                if is_real:
                    real_count += 1
                    status = "✅ REAL"
                else:
                    demo_count += 1
                    status = "🎭 DEMO"
                
                print(f"{i}. {status} - {name}")
                print(f"   {headline}")
                print(f"   {url}")
                print()
            
            print("📊 Summary:")
            print(f"   Real profiles: {real_count}")
            print(f"   Demo profiles: {demo_count}")
            print()
            
            if real_count > 0:
                print("🎉 SUCCESS! The enhanced search is using real LinkedIn profiles!")
                print("   You should now see real profiles in the web interface.")
            else:
                print("⚠️  Still showing demo profiles. Check the cache and search logic.")
                
        else:
            print("❌ No profiles found")
            
    except Exception as e:
        print(f"❌ Error testing enhanced search: {e}")
        import traceback
        traceback.print_exc()

def check_cache_status():
    """Check the current cache status"""
    print("\n📊 Cache Status")
    print("=" * 40)
    
    cache_path = Path("agent/cache.json")
    if cache_path.exists():
        try:
            with open(cache_path, "r") as f:
                cache_data = json.load(f)
            
            total_profiles = 0
            real_profiles = 0
            demo_profiles = 0
            
            for cache_key, profiles in cache_data.items():
                total_profiles += len(profiles)
                for profile in profiles:
                    if isinstance(profile, dict) and 'linkedin_url' in profile:
                        url = profile['linkedin_url']
                        if any(demo_suffix in url for demo_suffix in ['-ai', '-dev', '-eng', '-aws', '-ml']):
                            demo_profiles += 1
                        else:
                            real_profiles += 1
            
            print(f"Total profiles in cache: {total_profiles}")
            print(f"Real profiles: {real_profiles}")
            print(f"Demo profiles: {demo_profiles}")
            
            if real_profiles > 0:
                print("✅ Cache contains real profiles - enhanced search should use them!")
            else:
                print("⚠️  Cache only contains demo profiles")
                
        except Exception as e:
            print(f"Error reading cache: {e}")
    else:
        print("No cache file found")

def main():
    """Main function"""
    print("🚀 LinkedIn Sourcing Agent - Real Profiles Test")
    print("=" * 60)
    
    # Check cache status
    check_cache_status()
    
    # Test enhanced search
    test_enhanced_search()
    
    print("\n🎯 Next Steps:")
    print("   1. Go to http://localhost:8000")
    print("   2. Enter a job description")
    print("   3. You should now see real LinkedIn profiles!")
    print("   4. Click on the LinkedIn links to open real profiles")

if __name__ == "__main__":
    main() 