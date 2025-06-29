#!/usr/bin/env python3
"""
Setup Gemini API Key for Real LinkedIn Profiles
"""

import os
import sys
from pathlib import Path

def setup_gemini_key():
    """Set up the Gemini API key"""
    print("🔗 Setting up Gemini API Key for Real LinkedIn Profiles")
    print("=" * 60)
    
    # Set the API key as environment variable
    api_key = "AIzaSyA_rF9TDZruVbZC-XtQS71LAfphQLE6i7o"
    
    # Set environment variables
    os.environ["GEMINI_API_KEY"] = api_key
    os.environ["AI_PROVIDER"] = "gemini"
    os.environ["USE_GOOGLE_SEARCH"] = "true"
    os.environ["DEBUG"] = "true"
    
    print(f"✅ Gemini API Key configured: {api_key[:20]}...")
    print(f"✅ AI Provider: gemini")
    print(f"✅ Google Search: enabled")
    print(f"✅ Debug Mode: enabled")
    
    # Test the configuration
    test_configuration()
    
    return True

def test_configuration():
    """Test the configuration"""
    print("\n🔍 Testing Configuration...")
    
    try:
        # Import and test the config
        sys.path.append('agent')
        import config
        
        # Check if AI client can be created
        ai_client = config.get_ai_client()
        if ai_client:
            print("   ✅ AI Client: Successfully created")
        else:
            print("   ❌ AI Client: Failed to create")
        
        # Check available providers
        providers = config.get_available_ai_providers()
        print(f"   ✅ Available AI Providers: {providers}")
        
        # Check search client
        search_client = config.get_search_client()
        print(f"   ✅ Search Client: {search_client}")
        
        # Validate configuration
        issues = config.validate_config()
        if issues:
            print("   ❌ Configuration Issues:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print("   ✅ Configuration: Valid")
            
    except Exception as e:
        print(f"   ❌ Error testing configuration: {e}")

def show_real_profiles():
    """Show real profiles available in cache"""
    print("\n📊 Real Profiles Available")
    print("=" * 40)
    
    cache_path = Path("agent/cache.json")
    if cache_path.exists():
        try:
            import json
            with open(cache_path, "r") as f:
                cache_data = json.load(f)
            
            real_profiles = []
            for cache_key, profiles in cache_data.items():
                for profile in profiles:
                    if (isinstance(profile, dict) and 
                        'linkedin_url' in profile and 
                        not any(demo_suffix in profile['linkedin_url'] for demo_suffix in ['-ai', '-dev', '-eng', '-aws', '-ml'])):
                        real_profiles.append(profile)
            
            if real_profiles:
                print(f"   Found {len(real_profiles)} real LinkedIn profiles in cache:")
                for i, profile in enumerate(real_profiles[:5], 1):
                    print(f"   {i}. {profile.get('name', 'Unknown')} - {profile.get('headline', 'N/A')}")
                    print(f"      {profile.get('linkedin_url', 'N/A')}")
                    print()
                
                if len(real_profiles) > 5:
                    print(f"   ... and {len(real_profiles) - 5} more profiles")
                
                print("   ✅ These real profiles will be used when searching!")
            else:
                print("   No real profiles found in cache.")
                print("   🔍 The system will now search for fresh real profiles!")
                
        except Exception as e:
            print(f"   Error reading cache: {e}")
    else:
        print("   No cache file found.")
        print("   🔍 The system will search for fresh real profiles!")

def main():
    """Main function"""
    print("🚀 LinkedIn Sourcing Agent - Real Profiles Setup")
    print("=" * 60)
    
    # Set up the API key
    if setup_gemini_key():
        # Show available real profiles
        show_real_profiles()
        
        print("\n🎉 Setup Complete!")
        print("=" * 60)
        print("✅ Your Gemini API key is configured")
        print("✅ Real LinkedIn profile searching is enabled")
        print("✅ The system will now find real candidates")
        print("\n🚀 Starting the application...")
        print("   The system will use real profiles from cache or search for fresh ones!")
        
        # Start the application
        try:
            import subprocess
            subprocess.run([sys.executable, "start_agent.py"], env=os.environ)
        except KeyboardInterrupt:
            print("\n👋 Application stopped by user")
        except Exception as e:
            print(f"\n❌ Error starting application: {e}")
            print("   You can manually start it with: python start_agent.py")
    else:
        print("❌ Failed to set up API key")

if __name__ == "__main__":
    main() 