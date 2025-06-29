#!/usr/bin/env python3
"""
Quick setup script for Synapse LinkedIn Sourcing
"""
import os
import sys
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🚀 Synapse LinkedIn Sourcing - Quick Setup")
    print("=" * 60)
    print()

def create_env_file():
    """Create .env file with user input"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("📝 .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("Skipping .env file creation")
            return True
    
    print("\n🔑 API Key Configuration")
    print("You'll need at least one AI provider API key:")
    print("1. Google Gemini (Recommended - Free tier available)")
    print("2. OpenAI GPT-4 (Paid)")
    print("3. Anthropic Claude (Paid)")
    print()
    
    env_content = []
    
    # AI Provider selection
    print("Which AI provider would you like to use?")
    print("1. Google Gemini (Recommended)")
    print("2. OpenAI GPT-4")
    print("3. Anthropic Claude")
    print("4. Skip for now (use mock data)")
    
    while True:
        choice = input("Enter your choice (1-4): ").strip()
        if choice == "1":
            env_content.append("AI_PROVIDER=gemini")
            api_key = input("Enter your Google Gemini API key: ").strip()
            if api_key:
                env_content.append(f"GEMINI_API_KEY={api_key}")
            break
        elif choice == "2":
            env_content.append("AI_PROVIDER=openai")
            api_key = input("Enter your OpenAI API key: ").strip()
            if api_key:
                env_content.append(f"OPENAI_API_KEY={api_key}")
            break
        elif choice == "3":
            env_content.append("AI_PROVIDER=anthropic")
            api_key = input("Enter your Anthropic API key: ").strip()
            if api_key:
                env_content.append(f"ANTHROPIC_API_KEY={api_key}")
            break
        elif choice == "4":
            env_content.append("AI_PROVIDER=none")
            print("No AI provider configured. System will use mock data.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    # Search configuration
    print("\n🔍 Search Configuration")
    print("Choose your search method:")
    print("1. Google Search (Free, may be rate limited)")
    print("2. SerpAPI (Paid, more reliable)")
    print("3. Skip for now (use mock data)")
    
    search_choice = input("Enter your choice (1-3): ").strip()
    if search_choice == "2":
        serpapi_key = input("Enter your SerpAPI key: ").strip()
        if serpapi_key:
            env_content.extend([
                "USE_SERPAPI=true",
                f"SERPAPI_KEY={serpapi_key}"
            ])
    elif search_choice == "1":
        env_content.append("USE_GOOGLE_SEARCH=true")
    else:
        print("No search provider configured. System will use mock data.")
    
    # Additional configuration
    env_content.extend([
        "",
        "# LinkedIn Sourcing Configuration",
        "MAX_CANDIDATES_PER_SEARCH=25",
        "SEARCH_DELAY_SECONDS=2",
        "CACHE_DURATION_HOURS=24",
        "",
        "# API Configuration",
        "HOST=0.0.0.0",
        "PORT=8000",
        "",
        "# Rate Limiting",
        "SEARCH_RATE_LIMIT=10",
        "AI_RATE_LIMIT=50",
        "",
        "# Debug Mode (set to true for troubleshooting)",
        "DEBUG=false"
    ])
    
    # Write .env file
    try:
        with open(env_file, 'w') as f:
            f.write('\n'.join(env_content))
        print("✅ .env file created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def install_basic_dependencies():
    """Install basic dependencies"""
    print("📦 Installing basic dependencies...")
    
    basic_packages = [
        "fastapi",
        "uvicorn[standard]",
        "python-dotenv",
        "requests",
        "beautifulsoup4",
        "jinja2",
        "pydantic"
    ]
    
    try:
        import subprocess
        for package in basic_packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print("✅ Basic dependencies installed successfully")
        return True
    except Exception as e:
        print(f"⚠️  Some dependencies failed to install: {e}")
        print("You can install them manually later with: pip install fastapi uvicorn python-dotenv requests beautifulsoup4 jinja2 pydantic")
        return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Quick Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. 🚀 Start the application:")
    print("   cd agent")
    print("   python main.py")
    print()
    print("2. 🌐 Open your browser and go to:")
    print("   http://localhost:8000")
    print()
    print("3. 📝 Test with a job description like:")
    print("   'Senior Python Developer with 5+ years experience in Django and React'")
    print()
    print("4. 🔑 To enable real data:")
    print("   - Get a Google Gemini API key: https://makersuite.google.com/app/apikey")
    print("   - Add it to your .env file")
    print()
    print("5. 📚 Read the documentation:")
    print("   - REAL_DATA_SETUP.md - Detailed setup guide")
    print("   - MODERN_UI_GUIDE.md - UI customization")
    print("   - README_REAL_DATA.md - Complete guide")
    print()
    print("🔧 Troubleshooting:")
    print("- If you get API errors, check your API key in .env")
    print("- If search fails, try using SerpAPI for more reliable results")
    print("- Enable DEBUG=true in .env for detailed logs")
    print()
    print("💡 Tips:")
    print("- The system will use mock data if no API key is provided")
    print("- Real data requires valid API keys")
    print("- Cache is used to avoid duplicate searches")
    print()

def main():
    """Main setup function"""
    print_banner()
    
    # Install basic dependencies
    install_basic_dependencies()
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Print next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("✅ Quick setup completed successfully!")
        else:
            print("❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 