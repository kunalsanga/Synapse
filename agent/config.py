"""
Configuration settings for the LinkedIn Sourcing Agent
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AI Provider Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()  # gemini, openai, anthropic

# Google Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

# Anthropic Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")

# LinkedIn Sourcing Configuration
MAX_CANDIDATES_PER_SEARCH = int(os.getenv("MAX_CANDIDATES_PER_SEARCH", "25"))
SEARCH_DELAY_SECONDS = int(os.getenv("SEARCH_DELAY_SECONDS", "2"))
CACHE_DURATION_HOURS = int(os.getenv("CACHE_DURATION_HOURS", "24"))

# API Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Search Configuration
USE_GOOGLE_SEARCH = os.getenv("USE_GOOGLE_SEARCH", "true").lower() == "true"
USE_SERPAPI = os.getenv("USE_SERPAPI", "false").lower() == "true"
USE_LINKEDIN_API = os.getenv("USE_LINKEDIN_API", "false").lower() == "true"

# API Keys for search services
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
LINKEDIN_API_KEY = os.getenv("LINKEDIN_API_KEY")

# Rate Limiting
SEARCH_RATE_LIMIT = int(os.getenv("SEARCH_RATE_LIMIT", "10"))
AI_RATE_LIMIT = int(os.getenv("AI_RATE_LIMIT", "50"))

# Search Configuration
GOOGLE_SEARCH_URL = "https://www.google.com/search"
SERPAPI_URL = "https://serpapi.com/search"
LINKEDIN_DOMAIN = "linkedin.com/in"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Debug Mode
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Fit Score Weights
FIT_SCORE_WEIGHTS = {
    "education": 0.20,
    "trajectory": 0.20,
    "company": 0.15,
    "skills": 0.25,
    "location": 0.10,
    "tenure": 0.10
}

# File Paths - Fixed to use correct relative paths
DATA_FILE = "data.json"
CACHE_FILE = "cache.json"

# Message Generation Templates
OUTREACH_MESSAGE_TEMPLATE = """
Generate a personalized LinkedIn message to {name}, whose title is {headline}, based in {location}, 
referencing their background in {skills} and matching this job:

{job_description}

The message should be:
- Professional and friendly
- Specific to their background
- Under 200 words
- Include a clear call-to-action
- Avoid generic templates
"""

SCORING_PROMPT_TEMPLATE = """
Score this candidate (1-10) for the job description below based on these criteria:

Education (20%): Relevance of their educational background
Career Trajectory (20%): Progression and growth in their career
Company Relevance (15%): Quality and relevance of companies they've worked at
Experience Match (25%): Direct alignment with job requirements
Location Match (10%): Geographic fit for the role
Tenure (10%): Stability and commitment shown in roles

Candidate Profile:
- Name: {name}
- Headline: {headline}
- Location: {location}
- Experience: {experience}

Job Description:
{job_description}

Provide scores for each category and a brief explanation for each score.
"""

# AI Provider Functions
def get_ai_client():
    """Get the appropriate AI client based on configuration"""
    if AI_PROVIDER == "gemini" and GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            return genai.GenerativeModel(GEMINI_MODEL)
        except ImportError:
            print("Warning: google-generativeai not installed. Install with: pip install google-generativeai")
            return None
    elif AI_PROVIDER == "openai" and OPENAI_API_KEY:
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            return openai
        except ImportError:
            print("Warning: openai not installed. Install with: pip install openai")
            return None
    elif AI_PROVIDER == "anthropic" and ANTHROPIC_API_KEY:
        try:
            import anthropic
            return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        except ImportError:
            print("Warning: anthropic not installed. Install with: pip install anthropic")
            return None
    else:
        print(f"Warning: No valid AI provider configured. Available: {get_available_ai_providers()}")
        return None

def get_available_ai_providers():
    """Get list of available AI providers with API keys"""
    providers = []
    if GEMINI_API_KEY:
        providers.append("gemini")
    if OPENAI_API_KEY:
        providers.append("openai")
    if ANTHROPIC_API_KEY:
        providers.append("anthropic")
    return providers

def get_search_client():
    """Get the appropriate search client based on configuration"""
    if USE_SERPAPI and SERPAPI_KEY:
        return "serpapi"
    elif USE_LINKEDIN_API and LINKEDIN_API_KEY:
        return "linkedin"
    elif USE_GOOGLE_SEARCH:
        return "google"
    else:
        return "google"  # fallback

# Validation
def validate_config():
    """Validate the configuration and return any issues"""
    issues = []
    
    # Check AI provider
    if not get_ai_client():
        issues.append(f"No valid AI provider configured. Set AI_PROVIDER and corresponding API key.")
    
    # Check search provider
    search_client = get_search_client()
    if search_client == "serpapi" and not SERPAPI_KEY:
        issues.append("SerpAPI enabled but no API key provided")
    elif search_client == "linkedin" and not LINKEDIN_API_KEY:
        issues.append("LinkedIn API enabled but no API key provided")
    
    return issues

# Print configuration status
if DEBUG:
    print("=== Configuration Status ===")
    print(f"AI Provider: {AI_PROVIDER}")
    print(f"Available AI Providers: {get_available_ai_providers()}")
    print(f"Search Client: {get_search_client()}")
    print(f"Max Candidates: {MAX_CANDIDATES_PER_SEARCH}")
    print(f"Search Delay: {SEARCH_DELAY_SECONDS}s")
    print(f"Debug Mode: {DEBUG}")
    
    issues = validate_config()
    if issues:
        print("Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Configuration: ✅ Valid")
    print("==========================") 