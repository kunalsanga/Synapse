# Real Data Setup Guide for Synapse LinkedIn Sourcing

## 🎯 **Overview**
This guide will help you set up the Synapse LinkedIn Sourcing platform to work with real data instead of mock data. The platform can work with multiple AI providers and data sources.

## 🔑 **Required API Keys**

### **Option 1: Google Gemini (Recommended)**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to your `.env` file:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### **Option 2: OpenAI GPT-4**
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add to your `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### **Option 3: Anthropic Claude**
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create a new API key
3. Add to your `.env` file:
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## 📁 **Environment Setup**

### **Step 1: Create Environment File**
```bash
# Copy the example file
cp env_example.txt .env

# Edit the .env file with your API keys
nano .env
```

### **Step 2: Complete Environment Configuration**
```bash
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Alternative AI Providers (optional)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LinkedIn Sourcing Configuration
MAX_CANDIDATES_PER_SEARCH=25
SEARCH_DELAY_SECONDS=2
CACHE_DURATION_HOURS=24

# API Configuration
HOST=0.0.0.0
PORT=8000

# Search Configuration (optional)
USE_GOOGLE_SEARCH=true
USE_LINKEDIN_API=false
LINKEDIN_API_KEY=your_linkedin_api_key_here

# Rate Limiting
SEARCH_RATE_LIMIT=10
AI_RATE_LIMIT=50
```

## 🚀 **Quick Start with Real Data**

### **Method 1: Using Google Gemini (Easiest)**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp env_example.txt .env
# Edit .env with your GEMINI_API_KEY

# 3. Run the application
cd agent
python main.py
```

### **Method 2: Using OpenAI GPT-4**
```bash
# 1. Install OpenAI dependencies
pip install openai

# 2. Set up environment
echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env

# 3. Run the application
cd agent
python main.py
```

## 🔧 **Advanced Configuration**

### **Enhanced Search Options**

#### **Option A: Google Search (Current)**
- ✅ **Pros**: Free, no API key needed
- ❌ **Cons**: Rate limited, may be blocked
- **Setup**: Already configured

#### **Option B: LinkedIn API (Premium)**
- ✅ **Pros**: Official API, reliable data
- ❌ **Cons**: Requires LinkedIn Developer account, paid
- **Setup**: 
```bash
# Get LinkedIn API key from https://developer.linkedin.com/
LINKEDIN_API_KEY=your_linkedin_api_key_here
USE_LINKEDIN_API=true
```

#### **Option C: SerpAPI (Recommended for Production)**
- ✅ **Pros**: Reliable, high success rate
- ❌ **Cons**: Paid service ($50/month)
- **Setup**:
```bash
# Get API key from https://serpapi.com/
SERPAPI_KEY=your_serpapi_key_here
USE_SERPAPI=true
```

### **AI Provider Configuration**

#### **Google Gemini (Recommended)**
```python
# In config.py
AI_PROVIDER = "gemini"
GEMINI_MODEL = "gemini-1.5-flash"  # Fast and cost-effective
```

#### **OpenAI GPT-4**
```python
# In config.py
AI_PROVIDER = "openai"
OPENAI_MODEL = "gpt-4-turbo-preview"  # Most capable
```

#### **Anthropic Claude**
```python
# In config.py
AI_PROVIDER = "anthropic"
ANTHROPIC_MODEL = "claude-3-sonnet-20240229"  # Balanced
```

## 🌐 **Deployment Options**

### **Local Development**
```bash
# Run locally
cd agent
python main.py

# Access at http://localhost:8000
```

### **Docker Deployment**
```bash
# Build and run with Docker
docker build -t synapse-linkedin .
docker run -p 8000:8000 --env-file .env synapse-linkedin
```

### **Cloud Deployment**

#### **Heroku**
```bash
# Create Procfile
echo "web: cd agent && python main.py" > Procfile

# Deploy
heroku create your-app-name
heroku config:set GEMINI_API_KEY=your_key_here
git push heroku main
```

#### **Railway**
```bash
# Connect your GitHub repo
# Add environment variables in Railway dashboard
# Deploy automatically
```

#### **Vercel**
```bash
# Create vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "agent/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "agent/main.py"
    }
  ]
}
```

## 🔍 **Testing Real Data**

### **Test Script**
```python
# test_real_data.py
import requests
import json

def test_real_search():
    url = "http://localhost:8000/match"
    data = {
        "job_description": "Senior Python Developer with 5+ years experience in Django and React. Must be based in San Francisco or remote.",
        "max_candidates": 5
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    print(f"Found {result['candidates_found']} candidates")
    for candidate in result['top_candidates']:
        print(f"- {candidate['name']}: {candidate['fit_score']}/10")
        print(f"  LinkedIn: {candidate['linkedin_url']}")

if __name__ == "__main__":
    test_real_search()
```

### **API Testing**
```bash
# Test the API directly
curl -X POST "http://localhost:8000/match" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Senior Software Engineer with Python and AWS experience",
    "max_candidates": 3
  }'
```

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **1. "No API key found"**
```bash
# Check your .env file
cat .env

# Make sure the file is in the correct location
ls -la .env
```

#### **2. "Search failed, using mock data"**
- Check your internet connection
- Verify Google search is accessible
- Consider using SerpAPI for more reliable results

#### **3. "AI scoring failed"**
- Verify your API key is valid
- Check API quota/limits
- Try a different AI provider

#### **4. Rate limiting issues**
```bash
# Increase delays in .env
SEARCH_DELAY_SECONDS=5
AI_RATE_LIMIT=10
```

### **Debug Mode**
```bash
# Enable debug logging
export DEBUG=true
python main.py
```

## 📊 **Monitoring and Analytics**

### **Health Check**
```bash
curl http://localhost:8000/health
```

### **Statistics**
```bash
curl http://localhost:8000/stats
```

### **Logs**
```bash
# View application logs
tail -f logs/app.log
```

## 🔒 **Security Considerations**

### **API Key Security**
- Never commit API keys to version control
- Use environment variables
- Rotate keys regularly
- Monitor API usage

### **Rate Limiting**
- Implement proper rate limiting
- Respect API provider limits
- Use caching to reduce API calls

### **Data Privacy**
- Don't store sensitive candidate data
- Implement data retention policies
- Follow GDPR compliance

## 💰 **Cost Optimization**

### **API Cost Comparison**
| Provider | Cost per 1K requests | Best for |
|----------|---------------------|----------|
| Google Gemini | $0.15 | Budget-friendly |
| OpenAI GPT-4 | $0.03 | High quality |
| Anthropic Claude | $0.015 | Balanced |

### **Cost Reduction Tips**
1. Use caching to avoid duplicate searches
2. Implement smart rate limiting
3. Use cheaper models for simple tasks
4. Batch requests when possible

## 🎯 **Production Checklist**

- [ ] API keys configured
- [ ] Environment variables set
- [ ] Rate limiting configured
- [ ] Error handling implemented
- [ ] Logging enabled
- [ ] Monitoring set up
- [ ] Security measures in place
- [ ] Backup strategy defined
- [ ] Documentation updated
- [ ] Testing completed

## 📞 **Support**

If you encounter issues:
1. Check the troubleshooting section
2. Review the logs
3. Test with different API providers
4. Open an issue on GitHub

---

**🎉 Congratulations!** Your Synapse LinkedIn Sourcing platform is now ready to work with real data and can be used by anyone with proper API keys. 