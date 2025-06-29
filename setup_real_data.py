#!/usr/bin/env python3
"""
Quick setup script for Synapse LinkedIn Sourcing with real data
"""
import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🚀 Synapse LinkedIn Sourcing - Real Data Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

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
    
    while True:
        choice = input("Enter your choice (1-3): ").strip()
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
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    # Search configuration
    print("\n🔍 Search Configuration")
    print("Choose your search method:")
    print("1. Google Search (Free, may be rate limited)")
    print("2. SerpAPI (Paid, more reliable)")
    
    search_choice = input("Enter your choice (1-2): ").strip()
    if search_choice == "2":
        serpapi_key = input("Enter your SerpAPI key: ").strip()
        if serpapi_key:
            env_content.extend([
                "USE_SERPAPI=true",
                f"SERPAPI_KEY={serpapi_key}"
            ])
    else:
        env_content.append("USE_GOOGLE_SEARCH=true")
    
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

def test_configuration():
    """Test the configuration"""
    print("\n🧪 Testing configuration...")
    try:
        # Test imports
        import config
        print("✅ Configuration loaded successfully")
        
        # Test AI client
        ai_client = config.get_ai_client()
        if ai_client:
            print("✅ AI client initialized successfully")
        else:
            print("⚠️  AI client not available - check your API key")
        
        # Test search client
        search_client = config.get_search_client()
        print(f"✅ Search client: {search_client}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def create_startup_script():
    """Create a startup script"""
    script_content = """#!/bin/bash
# Startup script for Synapse LinkedIn Sourcing

echo "🚀 Starting Synapse LinkedIn Sourcing Agent..."
cd agent
python main.py
"""
    
    try:
        with open("start.sh", 'w') as f:
            f.write(script_content)
        os.chmod("start.sh", 0o755)
        print("✅ Startup script created (start.sh)")
        return True
    except Exception as e:
        print(f"❌ Failed to create startup script: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
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
    print("4. 📚 Read the documentation:")
    print("   - REAL_DATA_SETUP.md - Detailed setup guide")
    print("   - MODERN_UI_GUIDE.md - UI customization")
    print("   - README.md - General information")
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
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Test configuration
    if not test_configuration():
        print("⚠️  Configuration test failed, but you can still proceed")
    
    # Create startup script
    create_startup_script()
    
    # Print next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("✅ Setup completed successfully!")
        else:
            print("❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 