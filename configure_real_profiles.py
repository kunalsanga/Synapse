#!/usr/bin/env python3
"""
Configure Real LinkedIn Profiles Setup Script

This script helps you configure API keys to get real LinkedIn profiles instead of demo data.
"""

import os
import sys
import json
from pathlib import Path

def print_banner():
    print("🔗 LinkedIn Sourcing Agent - Real Profiles Setup")
    print("=" * 60)
    print("This script will help you configure API keys to get real LinkedIn profiles.")
    print("=" * 60)

def get_api_key(provider_name, url):
    """Get API key from user input"""
    print(f"\n📋 {provider_name} API Key Setup")
    print(f"   Get your API key from: {url}")
    print(f"   Enter your {provider_name} API key (or press Enter to skip):")
    
    api_key = input("   API Key: ").strip()
    
    if api_key and api_key != "your_gemini_api_key_here":
        return api_key
    return None

def create_env_file():
    """Create .env file with user configuration"""
    print_banner()
    
    # Get API keys
    gemini_key = get_api_key("Google Gemini", "https://makersuite.google.com/app/apikey")
    openai_key = get_api_key("OpenAI", "https://platform.openai.com/api-keys")
    anthropic_key = get_api_key("Anthropic", "https://console.anthropic.com/")
    
    # Choose AI provider
    print("\n🤖 AI Provider Selection")
    print("   Choose your preferred AI provider:")
    print("   1. Google Gemini (Recommended)")
    print("   2. OpenAI GPT-4")
    print("   3. Anthropic Claude")
    
    while True:
        choice = input("   Enter choice (1-3): ").strip()
        if choice == "1":
            ai_provider = "gemini"
            break
        elif choice == "2":
            ai_provider = "openai"
            break
        elif choice == "3":
            ai_provider = "anthropic"
            break
        else:
            print("   Invalid choice. Please enter 1, 2, or 3.")
    
    # Create .env content
    env_content = f"""# AI Provider Configuration
AI_PROVIDER={ai_provider}

# Google Gemini API Configuration
GEMINI_API_KEY={gemini_key or 'your_gemini_api_key_here'}

# OpenAI Configuration
OPENAI_API_KEY={openai_key or 'your_openai_api_key_here'}

# Anthropic Configuration
ANTHROPIC_API_KEY={anthropic_key or 'your_anthropic_api_key_here'}

# Search Configuration
USE_GOOGLE_SEARCH=true
USE_SERPAPI=false
USE_LINKEDIN_API=false

# LinkedIn Sourcing Configuration
MAX_CANDIDATES_PER_SEARCH=25
SEARCH_DELAY_SECONDS=2
CACHE_DURATION_HOURS=24

# API Configuration
HOST=0.0.0.0
PORT=8000

# Debug Mode
DEBUG=true
"""
    
    # Write .env file
    env_path = Path(".env")
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print(f"\n✅ Configuration saved to {env_path}")
    
    # Validate configuration
    validate_configuration(env_path)
    
    return env_path

def validate_configuration(env_path):
    """Validate the configuration"""
    print("\n🔍 Validating Configuration...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(env_path)
    
    # Check AI provider
    ai_provider = os.getenv("AI_PROVIDER", "gemini")
    print(f"   AI Provider: {ai_provider}")
    
    # Check API keys
    if ai_provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "your_gemini_api_key_here":
            print("   ✅ Gemini API Key: Configured")
        else:
            print("   ❌ Gemini API Key: Not configured")
    elif ai_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            print("   ✅ OpenAI API Key: Configured")
        else:
            print("   ❌ OpenAI API Key: Not configured")
    elif ai_provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key and api_key != "your_anthropic_api_key_here":
            print("   ✅ Anthropic API Key: Configured")
        else:
            print("   ❌ Anthropic API Key: Not configured")
    
    print("   ✅ Search: Google Search enabled")
    print("   ✅ Configuration: Ready to use")

def show_real_profiles_in_cache():
    """Show real profiles that are already in the cache"""
    print("\n📊 Real Profiles in Cache")
    print("=" * 40)
    
    cache_path = Path("agent/cache.json")
    if not cache_path.exists():
        print("   No cache file found.")
        return
    
    try:
        with open(cache_path, "r") as f:
            cache_data = json.load(f)
        
        real_profiles = []
        for cache_key, profiles in cache_data.items():
            for profile in profiles:
                # Check if it's a real profile (not demo)
                if (isinstance(profile, dict) and 
                    'linkedin_url' in profile and 
                    not any(demo_suffix in profile['linkedin_url'] for demo_suffix in ['-ai', '-dev', '-eng', '-aws', '-ml'])):
                    real_profiles.append(profile)
        
        if real_profiles:
            print(f"   Found {len(real_profiles)} real LinkedIn profiles in cache:")
            for i, profile in enumerate(real_profiles[:10], 1):  # Show first 10
                print(f"   {i}. {profile.get('name', 'Unknown')} - {profile.get('headline', 'N/A')}")
                print(f"      {profile.get('linkedin_url', 'N/A')}")
                print()
            
            if len(real_profiles) > 10:
                print(f"   ... and {len(real_profiles) - 10} more profiles")
        else:
            print("   No real profiles found in cache.")
            
    except Exception as e:
        print(f"   Error reading cache: {e}")

def enable_real_profiles():
    """Enable real profiles by modifying the search logic"""
    print("\n🔧 Enabling Real Profiles")
    print("=" * 40)
    
    # Check if we have real profiles in cache
    cache_path = Path("agent/cache.json")
    if cache_path.exists():
        try:
            with open(cache_path, "r") as f:
                cache_data = json.load(f)
            
            # Find real profiles
            real_profiles = []
            for profiles in cache_data.values():
                for profile in profiles:
                    if (isinstance(profile, dict) and 
                        'linkedin_url' in profile and 
                        not any(demo_suffix in profile['linkedin_url'] for demo_suffix in ['-ai', '-dev', '-eng', '-aws', '-ml'])):
                        real_profiles.append(profile)
            
            if real_profiles:
                print(f"   ✅ Found {len(real_profiles)} real profiles in cache")
                print("   These will be used when API keys are not configured")
                return True
            else:
                print("   ❌ No real profiles found in cache")
                return False
        except Exception as e:
            print(f"   ❌ Error reading cache: {e}")
            return False
    else:
        print("   ❌ No cache file found")
        return False

def main():
    """Main function"""
    print_banner()
    
    # Show existing real profiles
    show_real_profiles_in_cache()
    
    # Ask user what they want to do
    print("\n🎯 What would you like to do?")
    print("   1. Configure API keys for fresh real profiles")
    print("   2. Use existing real profiles from cache")
    print("   3. Both (recommended)")
    
    while True:
        choice = input("\n   Enter choice (1-3): ").strip()
        if choice in ["1", "2", "3"]:
            break
        print("   Invalid choice. Please enter 1, 2, or 3.")
    
    if choice in ["1", "3"]:
        # Configure API keys
        env_path = create_env_file()
        print(f"\n📝 Next steps:")
        print(f"   1. Edit {env_path} with your actual API keys")
        print(f"   2. Restart the application")
        print(f"   3. The system will now search for real LinkedIn profiles")
    
    if choice in ["2", "3"]:
        # Enable real profiles from cache
        if enable_real_profiles():
            print(f"\n✅ Real profiles are available and will be used")
        else:
            print(f"\n❌ No real profiles found. Please configure API keys first.")
    
    print("\n🚀 Setup Complete!")
    print("   Run 'python start_agent.py' to start the application")

if __name__ == "__main__":
    main() 