#!/usr/bin/env python3
"""
Startup script for the LinkedIn Sourcing Agent
"""
import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import requests
        import google.generativeai
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment configuration"""
    print("🔧 Checking environment configuration...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Creating from template...")
        if os.path.exists('env_example.txt'):
            with open('env_example.txt', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print("✅ Created .env file from template")
            print("📝 Please edit .env file and add your Gemini API key")
        else:
            print("❌ env_example.txt not found")
            return False
    
    # Check Gemini API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("⚠️  Gemini API key not configured")
        print("📝 Please add your Gemini API key to the .env file")
        print("   You can get one at: https://makersuite.google.com/app/apikey")
        return False
    else:
        print("✅ Gemini API key configured")
    
    return True

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting LinkedIn Sourcing Agent...")
    
    # Change to agent directory
    os.chdir('agent')
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, 'main.py'
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🤖 LinkedIn Sourcing Agent Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("\n📋 Setup Instructions:")
        print("1. Get a Gemini API key from https://makersuite.google.com/app/apikey")
        print("2. Edit the .env file and add your API key")
        print("3. Run this script again")
        sys.exit(1)
    
    # Start server
    print("\n🎯 Ready to start server!")
    print("The API will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 40)
    
    start_server()

if __name__ == "__main__":
    main() 