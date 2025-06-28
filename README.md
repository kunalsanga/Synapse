# 🤖 Autonomous AI LinkedIn Sourcing Agent

An intelligent AI agent that automatically finds, scores, and generates personalized outreach messages for LinkedIn candidates based on job descriptions.

## 🎯 Features

- **🔍 Smart LinkedIn Discovery**: Uses Google search to find relevant LinkedIn profiles
- **📊 AI-Powered Scoring**: Evaluates candidates using a comprehensive rubric (Education, Career Trajectory, Company Relevance, Skills Match, Location, Tenure)
- **💬 Personalized Messages**: Generates tailored outreach messages using GPT-4
- **⚡ FastAPI API**: RESTful API for easy integration
- **📈 Caching**: Intelligent caching to avoid duplicate searches
- **🎯 Batch Processing**: Support for multiple job descriptions

## 🏗️ Architecture

```
/agent
├── main.py          # FastAPI entrypoint
├── search.py        # LinkedIn profile discovery
├── parser.py        # Candidate data extraction
├── scorer.py        # Fit score calculation
├── messenger.py     # Outreach message generation
├── config.py        # Configuration and constants
├── data.json        # Results storage
└── cache.json       # Search cache
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `env_example.txt` to `.env` and add your OpenAI API key:

```bash
cp env_example.txt .env
```

Edit `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
MAX_CANDIDATES_PER_SEARCH=25
SEARCH_DELAY_SECONDS=2
```

### 3. Run the Application

```bash
cd agent
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Usage

### Find Candidates

```bash
curl -X POST "http://localhost:8000/match" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We are looking for a Senior Software Engineer with 5+ years of experience in Python, React, and AWS. The role is based in San Francisco and involves building scalable web applications.",
    "max_candidates": 10
  }'
```

### Response Format

```json
{
  "job_id": "job-abc12345",
  "candidates_found": 10,
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

## 🎯 Fit Score Rubric

Candidates are scored (1-10) based on:

| Category | Weight | Description |
|----------|--------|-------------|
| **Education** | 20% | Relevance of educational background |
| **Career Trajectory** | 20% | Progression and growth in career |
| **Company Relevance** | 15% | Quality and relevance of companies |
| **Skills Match** | 25% | Direct alignment with job requirements |
| **Location Match** | 10% | Geographic fit for the role |
| **Tenure** | 10% | Stability and commitment shown |

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | Your OpenAI API key |
| `MAX_CANDIDATES_PER_SEARCH` | 25 | Maximum candidates to find |
| `SEARCH_DELAY_SECONDS` | 2 | Delay between searches |
| `CACHE_DURATION_HOURS` | 24 | How long to cache results |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and API info |
| `/health` | GET | Detailed health status |
| `/match` | POST | Find and score candidates |
| `/results/{job_id}` | GET | Get results for specific job |
| `/stats` | GET | Application statistics |

## 🛠️ Development

### Project Structure

```
synapse/
├── agent/
│   ├── main.py          # FastAPI application
│   ├── search.py        # LinkedIn profile discovery
│   ├── parser.py        # Data extraction and enrichment
│   ├── scorer.py        # Candidate scoring logic
│   ├── messenger.py     # Message generation
│   ├── config.py        # Configuration
│   ├── data.json        # Results storage
│   └── cache.json       # Search cache
├── requirements.txt     # Python dependencies
├── env_example.txt      # Environment template
└── README.md           # This file
```

### Adding New Features

1. **New Search Sources**: Extend `search.py` to include GitHub, Twitter, etc.
2. **Custom Scoring**: Modify `scorer.py` to add new scoring criteria
3. **Message Templates**: Update `messenger.py` with new message styles
4. **Data Enrichment**: Enhance `parser.py` to extract more candidate data

## 🚀 Deployment

### Local Development

```bash
cd agent
python main.py
```

### Production (Hugging Face Spaces)

1. Create a new Space on Hugging Face
2. Upload your code
3. Set environment variables in Space settings
4. Deploy

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY agent/ ./agent/
EXPOSE 8000

CMD ["python", "agent/main.py"]
```

## 🔍 How It Works

### 1. Profile Discovery
- Extracts keywords from job description
- Builds Google search queries: `site:linkedin.com/in "python" "san francisco"`
- Parses search results to extract LinkedIn URLs

### 2. Data Enrichment
- Extracts skills, experience level, education hints
- Identifies companies and career trajectory
- Estimates tenure and location relevance

### 3. AI Scoring
- Uses GPT-4 to score candidates across 6 categories
- Falls back to rule-based scoring if AI unavailable
- Calculates weighted fit score

### 4. Message Generation
- Creates personalized outreach messages
- Adapts tone based on experience level
- Includes specific references to background

## 🎯 Use Cases

- **Recruitment Agencies**: Automate candidate sourcing
- **HR Teams**: Scale hiring efforts
- **Startups**: Find talent efficiently
- **Tech Companies**: Source specialized roles

## 🔒 Privacy & Ethics

- **Rate Limiting**: Built-in delays to respect search engines
- **Data Minimization**: Only stores necessary candidate data
- **Transparency**: Clear scoring methodology
- **Compliance**: Respects LinkedIn's terms of service

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: Create a GitHub issue
- **Documentation**: Check the API docs at `/docs`
- **Examples**: See the test cases in the code

---

**Built with ❤️ for the recruiting community** 