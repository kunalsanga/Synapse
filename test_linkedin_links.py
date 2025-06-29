#!/usr/bin/env python3
"""
Test LinkedIn Links Script
"""

import json
import webbrowser
import time
from pathlib import Path

def test_linkedin_links():
    """Test LinkedIn links from cache"""
    print("🔗 Testing LinkedIn Links")
    print("=" * 50)
    
    cache_path = Path("agent/cache.json")
    if not cache_path.exists():
        print("❌ No cache file found")
        return
    
    try:
        with open(cache_path, "r") as f:
            cache_data = json.load(f)
        
        real_profiles = []
        demo_profiles = []
        
        # Categorize profiles
        for cache_key, profiles in cache_data.items():
            for profile in profiles:
                if isinstance(profile, dict) and 'linkedin_url' in profile:
                    url = profile['linkedin_url']
                    if any(demo_suffix in url for demo_suffix in ['-ai', '-dev', '-eng', '-aws', '-ml']):
                        demo_profiles.append(profile)
                    else:
                        real_profiles.append(profile)
        
        print(f"📊 Found {len(real_profiles)} real profiles and {len(demo_profiles)} demo profiles")
        print()
        
        if real_profiles:
            print("✅ Real LinkedIn Profiles (should open):")
            for i, profile in enumerate(real_profiles[:5], 1):
                print(f"   {i}. {profile.get('name', 'Unknown')}")
                print(f"      {profile.get('linkedin_url', 'N/A')}")
                print(f"      {profile.get('headline', 'N/A')}")
                print()
            
            # Test opening a real profile
            if real_profiles:
                test_profile = real_profiles[0]
                test_url = test_profile['linkedin_url']
                print(f"🧪 Testing link opening for: {test_profile['name']}")
                print(f"   URL: {test_url}")
                
                try:
                    # Try to open in browser
                    webbrowser.open(test_url)
                    print("   ✅ Link opened in browser successfully!")
                except Exception as e:
                    print(f"   ❌ Error opening link: {e}")
        
        if demo_profiles:
            print("🎭 Demo Profiles (should show demo message):")
            for i, profile in enumerate(demo_profiles[:3], 1):
                print(f"   {i}. {profile.get('name', 'Unknown')}")
                print(f"      {profile.get('linkedin_url', 'N/A')}")
                print()
        
        print("💡 Troubleshooting Tips:")
        print("   1. Make sure popup blockers are disabled")
        print("   2. Check if your browser allows opening new tabs")
        print("   3. Try right-clicking and 'Open in new tab'")
        print("   4. Copy the URL and paste it manually in your browser")
        
    except Exception as e:
        print(f"❌ Error reading cache: {e}")

def check_browser_settings():
    """Check browser settings that might affect link opening"""
    print("\n🔍 Browser Settings Check")
    print("=" * 50)
    print("Common issues that prevent LinkedIn links from opening:")
    print()
    print("1. Popup Blockers:")
    print("   - Check if your browser is blocking popups")
    print("   - Look for a popup blocker icon in the address bar")
    print("   - Add localhost:8000 to allowed sites")
    print()
    print("2. Security Settings:")
    print("   - Some browsers block links from localhost")
    print("   - Try using http://127.0.0.1:8000 instead")
    print()
    print("3. Browser Extensions:")
    print("   - Disable ad blockers temporarily")
    print("   - Check if any extensions are blocking links")
    print()
    print("4. Manual Testing:")
    print("   - Right-click on a LinkedIn link")
    print("   - Select 'Open in new tab'")
    print("   - If that works, it's a popup blocker issue")

def main():
    """Main function"""
    print("🔗 LinkedIn Link Testing Tool")
    print("=" * 60)
    
    test_linkedin_links()
    check_browser_settings()
    
    print("\n🎯 Next Steps:")
    print("   1. Try clicking on LinkedIn links in the web interface")
    print("   2. If links don't open, check browser console for errors")
    print("   3. Try disabling popup blockers")
    print("   4. Use the manual URL copy feature if needed")

if __name__ == "__main__":
    main() 