"""
FastAPI entrypoint for the LinkedIn Sourcing Agent
"""
import json
import uuid
import os
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

# Use enhanced search instead of basic search
from enhanced_search import EnhancedLinkedInSearcher
from parser import CandidateParser
from scorer import CandidateScorer
from messenger import MessageGenerator
import config

# Initialize FastAPI app
app = FastAPI(
    title="LinkedIn Sourcing Agent",
    description="Autonomous AI agent for finding and scoring LinkedIn candidates",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")

# Initialize components with enhanced search
searcher = EnhancedLinkedInSearcher()
parser = CandidateParser()
scorer = CandidateScorer()
messenger = MessageGenerator()

# Pydantic models
class JobRequest(BaseModel):
    job_description: str = Field(..., min_length=10, description="Job description to search for candidates")
    max_candidates: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of candidates to return")
    job_id: Optional[str] = Field(None, description="Optional job ID for tracking")

class CandidateResponse(BaseModel):
    name: str
    linkedin_url: str
    fit_score: float
    score_breakdown: Dict[str, float]
    outreach_message: str
    headline: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    companies: Optional[List[str]] = None

class MatchResponse(BaseModel):
    job_id: str
    candidates_found: int
    top_candidates: List[CandidateResponse]
    search_metadata: Dict

# In-memory storage for results (in production, use a proper database)
job_results = {}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "LinkedIn Sourcing Agent API is running",
        "version": "1.0.0",
        "endpoints": {
            "POST /match": "Find and score candidates for a job description",
            "GET /health": "Health check",
            "GET /results/{job_id}": "Get results for a specific job",
            "GET /stats": "Application statistics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gemini_available": bool(config.GEMINI_API_KEY)
    }

@app.post("/match", response_model=MatchResponse)
async def match_candidates(request: JobRequest, background_tasks: BackgroundTasks):
    """
    Main endpoint to find and score candidates for a job description
    """
    try:
        # Generate job ID if not provided
        job_id = request.job_id or f"job-{uuid.uuid4().hex[:8]}"
        
        print(f"Starting candidate search for job ID: {job_id}")
        
        # Step 1: Search for LinkedIn profiles
        print("Step 1: Searching for LinkedIn profiles...")
        raw_profiles = searcher.search_linkedin_profiles(
            request.job_description, 
            request.max_candidates
        )
        
        if not raw_profiles:
            raise HTTPException(
                status_code=404, 
                detail="No LinkedIn profiles found for the given job description"
            )
        
        print(f"Found {len(raw_profiles)} raw profiles")
        
        # Step 2: Parse and enrich candidate data
        print("Step 2: Parsing and enriching candidate data...")
        enriched_candidates = parser.parse_candidates(raw_profiles, request.job_description)
        
        if not enriched_candidates:
            raise HTTPException(
                status_code=500, 
                detail="Failed to parse candidate data"
            )
        
        print(f"Enriched {len(enriched_candidates)} candidates")
        
        # Step 3: Score candidates
        print("Step 3: Scoring candidates...")
        scored_candidates = scorer.score_candidates(enriched_candidates, request.job_description)
        
        print(f"Scored {len(scored_candidates)} candidates")
        
        # Step 4: Generate outreach messages
        print("Step 4: Generating outreach messages...")
        candidates_with_messages = messenger.generate_outreach_messages(
            scored_candidates, 
            request.job_description
        )
        
        print(f"Generated messages for {len(candidates_with_messages)} candidates")
        
        # Step 5: Prepare response
        top_candidates = candidates_with_messages[:request.max_candidates]
        
        # Convert to response format
        candidate_responses = []
        for candidate in top_candidates:
            candidate_response = CandidateResponse(
                name=candidate.get('name', 'Unknown'),
                linkedin_url=candidate.get('linkedin_url', ''),
                fit_score=candidate.get('fit_score', 0.0),
                score_breakdown=candidate.get('score_breakdown', {}),
                outreach_message=candidate.get('outreach_message', ''),
                headline=candidate.get('headline'),
                location=candidate.get('location'),
                skills=candidate.get('skills'),
                companies=candidate.get('companies')
            )
            candidate_responses.append(candidate_response)
        
        # Prepare metadata
        search_metadata = {
            "total_profiles_found": len(raw_profiles),
            "enriched_candidates": len(enriched_candidates),
            "scored_candidates": len(scored_candidates),
            "search_timestamp": datetime.now().isoformat(),
            "job_description_length": len(request.job_description),
            "ai_scoring_used": bool(config.GEMINI_API_KEY)
        }
        
        # Store results
        job_results[job_id] = {
            "request": request.dict(),
            "response": {
                "job_id": job_id,
                "candidates_found": len(candidate_responses),
                "top_candidates": [c.dict() for c in candidate_responses],
                "search_metadata": search_metadata
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file (optional)
        background_tasks.add_task(save_results_to_file, job_id)
        
        print(f"Successfully processed job {job_id} with {len(candidate_responses)} candidates")
        
        return MatchResponse(
            job_id=job_id,
            candidates_found=len(candidate_responses),
            top_candidates=candidate_responses,
            search_metadata=search_metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in match endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/results/{job_id}")
async def get_job_results(job_id: str):
    """Get results for a specific job"""
    if job_id not in job_results:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_results[job_id]

@app.get("/stats")
async def get_stats():
    """Get application statistics"""
    total_jobs = len(job_results)
    total_candidates = sum(
        result["response"]["candidates_found"] 
        for result in job_results.values()
    )
    avg_candidates = total_candidates / total_jobs if total_jobs > 0 else 0
    
    return {
        "total_jobs": total_jobs,
        "total_candidates": total_candidates,
        "avg_candidates_per_job": round(avg_candidates, 1),
        "uptime": "Running",
        "last_updated": datetime.now().isoformat()
    }

def save_results_to_file(job_id: str):
    """Save results to JSON file"""
    try:
        if job_id in job_results:
            with open("data.json", "w") as f:
                json.dump(job_results, f, indent=2)
    except Exception as e:
        print(f"Error saving results: {e}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return {
        "error": "Internal server error",
        "detail": str(exc),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/hackathon", response_model=Dict)
async def hackathon_endpoint(request: JobRequest):
    """
    Hackathon-specific endpoint that returns top 10 candidates with personalized outreach
    Returns the exact format required for the competition
    """
    try:
        # Generate job ID
        job_id = request.job_id or f"hackathon-{uuid.uuid4().hex[:8]}"
        
        print(f"Processing hackathon request for job ID: {job_id}")
        
        # Step 1: Search for LinkedIn profiles
        print("Step 1: Searching for LinkedIn profiles...")
        raw_profiles = searcher.search_linkedin_profiles(
            request.job_description, 
            10  # Always return top 10 for hackathon
        )
        
        if not raw_profiles:
            return {
                "job_id": job_id,
                "candidates_found": 0,
                "top_candidates": [],
                "error": "No LinkedIn profiles found for the given job description"
            }
        
        print(f"Found {len(raw_profiles)} raw profiles")
        
        # Step 2: Parse and enrich candidate data
        print("Step 2: Parsing and enriching candidate data...")
        enriched_candidates = parser.parse_candidates(raw_profiles, request.job_description)
        
        if not enriched_candidates:
            return {
                "job_id": job_id,
                "candidates_found": 0,
                "top_candidates": [],
                "error": "Failed to parse candidate data"
            }
        
        print(f"Enriched {len(enriched_candidates)} candidates")
        
        # Step 3: Score candidates using hackathon rubric
        print("Step 3: Scoring candidates using hackathon rubric...")
        scored_candidates = scorer.score_candidates(enriched_candidates, request.job_description)
        
        print(f"Scored {len(scored_candidates)} candidates")
        
        # Step 4: Generate personalized outreach messages
        print("Step 4: Generating personalized outreach messages...")
        candidates_with_messages = messenger.generate_outreach_messages(
            scored_candidates, 
            request.job_description
        )
        
        print(f"Generated messages for {len(candidates_with_messages)} candidates")
        
        # Step 5: Prepare hackathon response format
        top_candidates = candidates_with_messages[:10]  # Top 10 candidates
        
        # Convert to hackathon format
        hackathon_candidates = []
        for candidate in top_candidates:
            hackathon_candidate = {
                "name": candidate.get('name', 'Unknown'),
                "linkedin_url": candidate.get('linkedin_url', ''),
                "fit_score": candidate.get('fit_score', 0.0),
                "score_breakdown": candidate.get('score_breakdown', {}),
                "outreach_message": candidate.get('outreach_message', ''),
                "headline": candidate.get('headline', ''),
                "location": candidate.get('location', ''),
                "skills": candidate.get('skills', []),
                "companies": candidate.get('companies', []),
                "education": candidate.get('education', [])
            }
            hackathon_candidates.append(hackathon_candidate)
        
        # Prepare hackathon response
        response = {
            "job_id": job_id,
            "candidates_found": len(hackathon_candidates),
            "top_candidates": hackathon_candidates,
            "job_description": request.job_description,
            "processing_timestamp": datetime.now().isoformat(),
            "scoring_method": "Hackathon Rubric (Education 20%, Trajectory 20%, Company 15%, Skills 25%, Location 10%, Tenure 10%)"
        }
        
        # Store results
        job_results[job_id] = {
            "request": request.dict(),
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "type": "hackathon"
        }
        
        print(f"Successfully processed hackathon request {job_id} with {len(hackathon_candidates)} candidates")
        
        return response
        
    except Exception as e:
        print(f"Error in hackathon endpoint: {e}")
        return {
            "job_id": job_id if 'job_id' in locals() else "error",
            "candidates_found": 0,
            "top_candidates": [],
            "error": str(e)
        }

if __name__ == "__main__":
    print("Starting LinkedIn Sourcing Agent...")
    print("Gemini API configured:", bool(config.GEMINI_API_KEY))
    print("Server will run on 0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 