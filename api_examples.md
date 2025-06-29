# 🤖 LinkedIn Sourcing Agent - API Examples

This document provides practical examples of how to use the LinkedIn Sourcing Agent API.

## 🚀 Quick Start

The API is running at `http://localhost:8000`

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. API Information
```bash
curl http://localhost:8000/
```

## 🎯 Main Features

### 1. Find Candidates for a Job

**Example: Senior Software Engineer**
```bash
curl -X POST "http://localhost:8000/match" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We are looking for a Senior Software Engineer with 5+ years of experience in Python, React, and AWS. The role is based in San Francisco and involves building scalable web applications. Must have experience with microservices architecture and cloud deployment.",
    "max_candidates": 5
  }'
```

**Example: Data Scientist**
```bash
curl -X POST "http://localhost:8000/match" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Seeking a Data Scientist with expertise in machine learning, Python, and SQL. The role involves developing predictive models, analyzing large datasets, and working with stakeholders to drive business decisions. Experience with TensorFlow or PyTorch preferred.",
    "max_candidates": 3
  }'
```

**Example: Product Manager**
```bash
curl -X POST "http://localhost:8000/match" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Looking for a Product Manager with 3+ years of experience in SaaS products. Must have strong analytical skills, experience with user research, and ability to work with engineering teams. Experience with agile methodologies and product analytics tools required.",
    "max_candidates": 4
  }'
```

### 2. Retrieve Results for a Specific Job

Replace `{job_id}` with the actual job ID returned from the match endpoint:
```bash
curl http://localhost:8000/results/{job_id}
```

### 3. Get Application Statistics
```bash
curl http://localhost:8000/stats
```

## 📊 Expected Response Format

When you call the `/match` endpoint, you'll get a response like this:

```json
{
  "job_id": "job-abc12345",
  "candidates_found": 5,
  "top_candidates": [
    {
      "name": "Jane Smith",
      "linkedin_url": "https://linkedin.com/in/janesmith",
      "fit_score": 8.5,
      "score_breakdown": {
        "education": 9.0,
        "trajectory": 8.0,
        "company": 8.5,
        "skills": 9.0,
        "location": 10.0,
        "tenure": 7.0
      },
      "outreach_message": "Hi Jane, I noticed your impressive background in Python and React at Google...",
      "headline": "Senior Software Engineer at Google",
      "location": "San Francisco, CA",
      "skills": ["python", "react", "aws", "javascript"],
      "companies": ["google", "microsoft"]
    }
  ],
  "search_metadata": {
    "total_profiles_found": 25,
    "enriched_candidates": 20,
    "scored_candidates": 20,
    "search_timestamp": "2024-01-15T10:30:00",
    "job_description_length": 245,
    "ai_scoring_used": true
  }
}
```

## 🎯 Scoring Breakdown

Each candidate is scored (1-10) based on:

| Category | Weight | Description |
|----------|--------|-------------|
| **Education** | 20% | Relevance of educational background |
| **Career Trajectory** | 20% | Progression and growth in career |
| **Company Relevance** | 15% | Quality and relevance of companies |
| **Skills Match** | 25% | Direct alignment with job requirements |
| **Location Match** | 10% | Geographic fit for the role |
| **Tenure** | 10% | Stability and commitment shown |

## 🔧 PowerShell Examples

If you're using PowerShell on Windows:

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get

# Find candidates
$body = @{
    job_description = "We are looking for a Senior Software Engineer with 5+ years of experience in Python, React, and AWS."
    max_candidates = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/match" -Method Post -Body $body -ContentType "application/json"
```

## 🌐 Web Interface

You can also access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 Python Examples

```python
import requests

# Find candidates
response = requests.post("http://localhost:8000/match", json={
    "job_description": "Senior Software Engineer with Python and React experience",
    "max_candidates": 5
})

if response.status_code == 200:
    data = response.json()
    print(f"Found {data['candidates_found']} candidates")
    
    for candidate in data['top_candidates']:
        print(f"{candidate['name']}: {candidate['fit_score']}/10")
        print(f"Message: {candidate['outreach_message'][:100]}...")
```

## ⚠️ Important Notes

1. **API Key Required**: Make sure you have configured your Gemini API key in the `.env` file
2. **Rate Limiting**: The API includes delays between searches to be respectful to external services
3. **Caching**: Results are cached to avoid duplicate searches
4. **Maximum Candidates**: Limited to 50 candidates per request for performance reasons

## 🎉 Try It Now!

Run the demonstration script to see all features in action:
```bash
python demo_features.py
``` 