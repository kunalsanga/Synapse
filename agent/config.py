"""
Configuration settings for the LinkedIn Sourcing Agent
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"  # or "gemini-1.5-pro" for more advanced tasks

# LinkedIn Sourcing Configuration
MAX_CANDIDATES_PER_SEARCH = int(os.getenv("MAX_CANDIDATES_PER_SEARCH", "25"))
SEARCH_DELAY_SECONDS = int(os.getenv("SEARCH_DELAY_SECONDS", "2"))
CACHE_DURATION_HOURS = int(os.getenv("CACHE_DURATION_HOURS", "24"))

# API Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Search Configuration
GOOGLE_SEARCH_URL = "https://www.google.com/search"
LINKEDIN_DOMAIN = "linkedin.com/in"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

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