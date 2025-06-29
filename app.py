"""
Hugging Face Spaces Deployment for Synapse Hackathon
"""
import os
import sys
from pathlib import Path

# Add the agent directory to the path
sys.path.append(str(Path(__file__).parent / "agent"))

# Import the FastAPI app
from main import app

# Set environment variables for Hugging Face Spaces
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("GOOGLE_API_KEY", "")
os.environ.setdefault("SERPAPI_KEY", "")

# Export the app for Hugging Face Spaces
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860) 