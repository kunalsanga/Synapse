# 🚀 Deployment Guide

This guide covers deploying the LinkedIn Sourcing Agent to various platforms.

## 🌐 Hugging Face Spaces

### 1. Create a New Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose "Docker" as the SDK
4. Set visibility (Public or Private)
5. Click "Create Space"

### 2. Configure Space Settings

In your Space settings, add these environment variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
MAX_CANDIDATES_PER_SEARCH=25
SEARCH_DELAY_SECONDS=2
CACHE_DURATION_HOURS=24
HOST=0.0.0.0
PORT=7860
```

### 3. Create Dockerfile

Create a `Dockerfile` in your Space:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent/ ./agent/

# Create necessary directories
RUN mkdir -p /app/agent

# Expose port (Hugging Face uses 7860)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Start the application
CMD ["python", "agent/main.py"]
```

### 4. Create app.py (Alternative to Dockerfile)

If you prefer using `app.py` instead of Dockerfile:

```python
import os
import sys
from pathlib import Path

# Add agent directory to path
sys.path.append(str(Path(__file__).parent / "agent"))

from agent.main import app

# Hugging Face Spaces expects the app to be named 'app'
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
```

### 5. Create requirements.txt

Ensure your `requirements.txt` is in the root directory:

```txt
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
beautifulsoup4==4.12.2
openai==1.3.7
python-dotenv==1.0.0
pydantic==2.5.0
aiofiles==23.2.1
python-multipart==0.0.6
```

### 6. Upload Files

Upload these files to your Space:
- `agent/` directory (all Python files)
- `requirements.txt`
- `Dockerfile` or `app.py`
- `README.md`

### 7. Deploy

Your Space will automatically build and deploy. The API will be available at:
`https://your-username-your-space-name.hf.space`

## 🐳 Docker Deployment

### Local Docker

```bash
# Build the image
docker build -t linkedin-sourcing-agent .

# Run the container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_api_key \
  linkedin-sourcing-agent
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  linkedin-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MAX_CANDIDATES_PER_SEARCH=25
      - SEARCH_DELAY_SECONDS=2
    volumes:
      - ./agent/data.json:/app/agent/data.json
      - ./agent/cache.json:/app/agent/cache.json
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## ☁️ Cloud Deployment

### Heroku

1. Create `Procfile`:
```
web: python agent/main.py
```

2. Deploy:
```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_api_key
git push heroku main
```

### Railway

1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Deploy automatically

### Render

1. Create a new Web Service
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python agent/main.py`
5. Add environment variables

## 🔧 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | Your OpenAI API key |
| `MAX_CANDIDATES_PER_SEARCH` | No | 25 | Max candidates per search |
| `SEARCH_DELAY_SECONDS` | No | 2 | Delay between searches |
| `CACHE_DURATION_HOURS` | No | 24 | Cache duration |
| `HOST` | No | 0.0.0.0 | Server host |
| `PORT` | No | 8000 | Server port |

## 🔒 Security Considerations

### Production Deployment

1. **API Key Security**:
   - Never commit API keys to version control
   - Use environment variables or secret management
   - Rotate keys regularly

2. **Rate Limiting**:
   - Implement rate limiting for API endpoints
   - Monitor usage to prevent abuse

3. **CORS Configuration**:
   - Restrict CORS origins in production
   - Update `main.py` CORS settings

4. **Data Privacy**:
   - Implement data retention policies
   - Secure storage of candidate data
   - GDPR compliance if applicable

### Example Production CORS Settings

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📊 Monitoring

### Health Checks

The application includes health check endpoints:
- `GET /health` - Basic health status
- `GET /stats` - Application statistics

### Logging

Add logging configuration to `main.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Metrics

Consider adding metrics collection:
- Request count
- Response times
- Error rates
- API usage

## 🚀 Performance Optimization

### Caching

- Results are cached in `cache.json`
- Implement Redis for distributed caching
- Set appropriate cache TTL

### Rate Limiting

- Built-in delays between searches
- Consider implementing request rate limiting
- Monitor API usage

### Scaling

- Use load balancers for multiple instances
- Implement database for persistent storage
- Consider async processing for large batches

## 🔍 Troubleshooting

### Common Issues

1. **OpenAI API Errors**:
   - Check API key validity
   - Verify account has credits
   - Check rate limits

2. **Search Failures**:
   - Google may block requests
   - Implement proxy rotation
   - Add more delays

3. **Memory Issues**:
   - Reduce `MAX_CANDIDATES_PER_SEARCH`
   - Implement pagination
   - Monitor memory usage

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 📞 Support

For deployment issues:
1. Check application logs
2. Verify environment variables
3. Test locally first
4. Check platform-specific documentation

---

**Happy Deploying! 🚀** 