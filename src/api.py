"""
FastAPI Application for HR Resume-Job Matching System
Stage 5: API Gateway

Endpoints:
- POST /match - Match a profile against jobs
- GET /jobs - List all available jobs
- GET /jobs/{job_id} - Get specific job
- GET /health - Health check
- POST /parse-profile - Parse CV text only
"""
import sys
import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, File, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import project modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.agent1_parser import RawParser
from agents.agent2_extractor import NLP_Extractor
from agents.agent3_scorer import Agent3Scorer
from agents.agent4_decision import DecisionEngine
from agents.agent5_analytics import AnalyticsEngine

# ============================================
# Pydantic Models
# ============================================

class ProfileInput(BaseModel):
    """Input model for profile text."""
    profile_text: str = Field(..., description="Raw CV/resume text")
    profile_id: Optional[str] = Field(None, description="Optional profile identifier")

class MatchRequest(BaseModel):
    """Request model for matching."""
    profile_text: str = Field(..., description="Raw CV/resume text")
    top_k: int = Field(10, description="Number of top matches to return", ge=1, le=50)
    make_decisions: bool = Field(True, description="Whether to make hiring decisions")
    profile_id: Optional[str] = Field(None, description="Optional profile identifier")

class SkillMatch(BaseModel):
    """Skill match information."""
    matched_skills: List[str]
    missing_skills: List[str]
    skill_match_score: float

class MatchResult(BaseModel):
    """Single match result."""
    job_id: str
    job_title: str
    match_label: str
    confidence: float
    decision: Optional[str] = None
    explanation: Optional[str] = None
    skill_match: SkillMatch
    experience_match_score: float
    warnings: List[str] = []
    ranking: Optional[int] = None

class MatchResponse(BaseModel):
    """Response model for matching."""
    profile_id: str
    candidate_name: str
    total_jobs_scored: int
    top_matches: List[MatchResult]
    processing_time_seconds: float

class JobResponse(BaseModel):
    """Job information response."""
    job_id: str
    job_title: str
    role_category: str
    skills_required: List[str]
    experience_required: Dict[str, int]
    description: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    agents_loaded: Dict[str, bool]
    llm_enabled: bool
    jobs_loaded: int

# ============================================
# FastAPI App Initialization
# ============================================

app = FastAPI(
    title="HR Resume-Job Matching API",
    description="Multi-agent system for intelligent resume-job matching",
    version="1.0.0",
    docs_url="/docs" if os.getenv('API_DOCS_ENABLED', 'true').lower() == 'true' else None
)

# CORS Configuration
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:8501').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Global State
# ============================================

class AppState:
    """Application state container."""
    def __init__(self):
        self.agent1_parser: Optional[RawParser] = None
        self.agent2_extractor: Optional[NLP_Extractor] = None
        self.agent3_scorer: Optional[Agent3Scorer] = None
        self.agent4_decision: Optional[DecisionEngine] = None
        self.agent5_analytics: Optional[AnalyticsEngine] = None
        self.jobs_data: List[Dict] = []
        self.jobs_loaded = False

state = AppState()

# ============================================
# Startup/Shutdown Events
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize agents and load data on startup."""
    print("\n" + "="*70)
    print("🚀 Starting HR Matching API")
    print("="*70)
    
    try:
        # Initialize Agent 1 (Parser)
        print("\n📝 Initializing Agent 1 (Parser)...")
        state.agent1_parser = RawParser()
        
        # Initialize Agent 2 (Extractor)
        print("\n🔍 Initializing Agent 2 (Extractor)...")
        state.agent2_extractor = NLP_Extractor()
        
        # Initialize Agent 3 (Scorer)
        print("\n🤖 Initializing Agent 3 (Scorer)...")
        state.agent3_scorer = Agent3Scorer()
        
        # Initialize Agent 4 (Decision Engine)
        print("\n🎯 Initializing Agent 4 (Decision Engine)...")
        state.agent4_decision = DecisionEngine()
        
        # Initialize Agent 5 (Analytics)
        print("\n📊 Initializing Agent 5 (Analytics)...")
        state.agent5_analytics = AnalyticsEngine(use_llm=True)
        
        # Load jobs data
        print("\n💼 Loading jobs data...")
        jobs_path = Path(os.getenv('JOBS_DATA_PATH', 'data/json/jobs.json'))
        if jobs_path.exists():
            with open(jobs_path, 'r', encoding='utf-8') as f:
                state.jobs_data = json.load(f)
            state.jobs_loaded = True
            print(f"   ✅ Loaded {len(state.jobs_data)} jobs")
        else:
            print(f"   ⚠️  Warning: Jobs file not found at {jobs_path}")
            state.jobs_data = []
        
        print("\n" + "="*70)
        print("✅ API Ready!")
        print(f"   Agents Loaded: 5/5")
        print(f"   Jobs Loaded: {len(state.jobs_data)}")
        print(f"   LLM Enabled: {state.agent3_scorer.llm_enabled if state.agent3_scorer else False}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("\n👋 Shutting down HR Matching API...")

# ============================================
# API Endpoints
# ============================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "HR Resume-Job Matching API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        agents_loaded={
            "agent1_parser": state.agent1_parser is not None,
            "agent2_extractor": state.agent2_extractor is not None,
            "agent3_scorer": state.agent3_scorer is not None,
            "agent4_decision": state.agent4_decision is not None,
            "agent5_analytics": state.agent5_analytics is not None
        },
        llm_enabled=state.agent3_scorer.llm_enabled if state.agent3_scorer else False,
        jobs_loaded=len(state.jobs_data)
    )

@app.get("/jobs", response_model=List[JobResponse], tags=["Jobs"])
async def list_jobs(
    category: Optional[str] = None,
    limit: int = 100
):
    """
    List all available jobs.
    
    Args:
        category: Optional filter by role category
        limit: Maximum number of jobs to return
    """
    if not state.jobs_loaded:
        raise HTTPException(status_code=503, detail="Jobs data not loaded")
    
    jobs = state.jobs_data
    
    # Filter by category if specified
    if category:
        jobs = [j for j in jobs if j.get('role_category', '').lower() == category.lower()]
    
    # Limit results
    jobs = jobs[:limit]
    
    # Format response
    response = []
    for job in jobs:
        exp = job.get('experience', {})
        response.append(JobResponse(
            job_id=job.get('job_id', 'unknown'),
            job_title=job.get('job_title', 'Unknown'),
            role_category=job.get('role_category', 'Unknown'),
            skills_required=job.get('skills', []),
            experience_required={
                "min_years": exp.get('min_years', 0) if isinstance(exp, dict) else 0,
                "max_years": exp.get('max_years', 99) if isinstance(exp, dict) else 99
            },
            description=job.get('description', None)
        ))
    
    return response

@app.get("/jobs/{job_id}", response_model=JobResponse, tags=["Jobs"])
async def get_job(job_id: str):
    """Get specific job by ID."""
    if not state.jobs_loaded:
        raise HTTPException(status_code=503, detail="Jobs data not loaded")
    
    # Find job
    job = next((j for j in state.jobs_data if j.get('job_id') == job_id), None)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    exp = job.get('experience', {})
    return JobResponse(
        job_id=job.get('job_id', 'unknown'),
        job_title=job.get('job_title', 'Unknown'),
        role_category=job.get('role_category', 'Unknown'),
        skills_required=job.get('skills', []),
        experience_required={
            "min_years": exp.get('min_years', 0) if isinstance(exp, dict) else 0,
            "max_years": exp.get('max_years', 99) if isinstance(exp, dict) else 99
        },
        description=job.get('description', None)
    )

@app.post("/parse-profile", tags=["Parsing"])
async def parse_profile(request: ProfileInput):
    """
    Parse a CV/resume text into structured format.
    
    Returns parsed profile without matching against jobs.
    """
    if not state.agent1_parser or not state.agent2_extractor:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    
    try:
        # Generate profile ID if not provided
        profile_id = request.profile_id or f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Step 1: Raw parsing
        raw_profile = state.agent1_parser.parse_profile(
            request.profile_text,
            profile_id=profile_id
        )
        
        # Step 2: NLP extraction
        structured_profile = state.agent2_extractor.process_profile(raw_profile)
        
        return {
            "profile_id": profile_id,
            "parsed_profile": structured_profile
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing profile: {str(e)}")

@app.post("/match", response_model=MatchResponse, tags=["Matching"])
async def match_profile(request: MatchRequest):
    """
    Match a profile against all jobs and return top matches.
    
    This is the main endpoint that runs the full pipeline:
    1. Parse profile (Agent 1 + 2)
    2. Score against all jobs (Agent 3)
    3. Make hiring decisions (Agent 4)
    4. Rank and return top matches
    """
    if not all([state.agent1_parser, state.agent2_extractor, state.agent3_scorer, state.agent4_decision]):
        raise HTTPException(status_code=503, detail="Agents not initialized")
    
    if not state.jobs_loaded:
        raise HTTPException(status_code=503, detail="Jobs data not loaded")
    
    start_time = datetime.now()
    
    try:
        # Generate profile ID if not provided
        profile_id = request.profile_id or f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n{'='*70}")
        print(f"🔄 Processing Match Request: {profile_id}")
        print(f"{'='*70}")
        
        # Step 1: Parse profile
        print("\n📝 Step 1: Parsing profile...")
        raw_profile = state.agent1_parser.parse_profile(
            request.profile_text,
            profile_id=profile_id
        )
        
        structured_profile = state.agent2_extractor.process_profile(raw_profile)
        print(f"   ✅ Profile parsed: {structured_profile.get('name', 'Unknown')}")
        
        # Step 2 & 3: Score and decide
        print(f"\n🤖 Step 2-3: Scoring against {len(state.jobs_data)} jobs...")
        
        if request.make_decisions:
            # Use Agent 4 for full decision pipeline
            results = []
            for job in state.jobs_data:
                # Score with Agent 3
                score = state.agent3_scorer.score_match(
                    structured_profile,
                    job,
                    verbose=False
                )
                
                # Make decision with Agent 4
                decision = state.agent4_decision.make_decision(
                    structured_profile,
                    job,
                    score,
                    generate_explanation=True,
                    verbose=False
                )
                decision["job_data"] = job
                results.append(decision)
            
            # Rank results
            results = state.agent4_decision.rank_candidates(results)
            
        else:
            # Just scoring, no decisions
            results = state.agent3_scorer.batch_score(
                structured_profile,
                state.jobs_data,
                top_k=len(state.jobs_data)
            )
        
        # Step 4: Format top matches
        print(f"\n📊 Step 4: Formatting top {request.top_k} matches...")
        top_matches = []
        
        for result in results[:request.top_k]:
            job_data = result.get("job_data", {})
            
            match = MatchResult(
                job_id=job_data.get("job_id", "unknown"),
                job_title=job_data.get("job_title", job_data.get("title", "Unknown")),
                match_label=result.get("match_label", "Unknown"),
                confidence=result.get("confidence", 0.0),
                decision=result.get("decision") if request.make_decisions else None,
                explanation=result.get("explanation") if request.make_decisions else None,
                skill_match=SkillMatch(
                    matched_skills=result.get("key_strengths", []),
                    missing_skills=result.get("key_gaps", []),
                    skill_match_score=result.get("skill_match_score", 0.0)
                ),
                experience_match_score=result.get("experience_match_score", 0.0),
                warnings=result.get("warnings", []),
                ranking=result.get("ranking")
            )
            top_matches.append(match)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        print(f"\n✅ Match request completed in {processing_time:.2f}s")
        print(f"{'='*70}\n")
        
        return MatchResponse(
            profile_id=profile_id,
            candidate_name=structured_profile.get("name", "Unknown Candidate"),
            total_jobs_scored=len(state.jobs_data),
            top_matches=top_matches,
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        print(f"\n❌ Error processing match request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing match: {str(e)}")

# ============================================
# Analytics Endpoints (Agent 5)
# ============================================

@app.get("/analytics/metrics", tags=["Analytics"])
async def get_analytics_metrics(batch_id: Optional[str] = None):
    """
    Get analytics metrics from decision logs.
    
    Args:
        batch_id: Optional specific batch to analyze (None = all batches)
    
    Returns:
        Analytics metrics including decision distribution, confidence scores, etc.
    """
    if not state.agent5_analytics:
        raise HTTPException(status_code=503, detail="Analytics agent not initialized")
    
    try:
        # Load decisions
        decisions = state.agent5_analytics.load_decisions(batch_id=batch_id)
        
        if not decisions:
            return {
                "message": "No decisions found",
                "total_decisions": 0
            }
        
        # Calculate metrics
        metrics = state.agent5_analytics.calculate_metrics(decisions)
        
        return {
            "total_decisions": len(decisions),
            "metrics": metrics,
            "batch_id": batch_id or "all"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating metrics: {str(e)}")

@app.get("/analytics/insights", tags=["Analytics"])
async def get_analytics_insights(batch_id: Optional[str] = None):
    """
    Get AI-generated insights from decision data.
    
    Uses Agent 5's local LLM to generate optimization recommendations.
    """
    if not state.agent5_analytics:
        raise HTTPException(status_code=503, detail="Analytics agent not initialized")
    
    try:
        # Load decisions
        decisions = state.agent5_analytics.load_decisions(batch_id=batch_id)
        
        if not decisions:
            return {
                "message": "No decisions found to analyze",
                "insights": "Insufficient data for insights generation"
            }
        
        # Calculate metrics
        metrics = state.agent5_analytics.calculate_metrics(decisions)
        
        # Generate insights
        insights = state.agent5_analytics.generate_insights(metrics, decisions)
        
        return {
            "total_decisions": len(decisions),
            "insights": insights,
            "batch_id": batch_id or "all"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@app.post("/analytics/generate-report", tags=["Analytics"])
async def generate_analytics_report(batch_id: Optional[str] = None):
    """
    Generate full analytics report with visualizations.
    
    Creates HTML dashboard and JSON summary in the reports directory.
    """
    if not state.agent5_analytics:
        raise HTTPException(status_code=503, detail="Analytics agent not initialized")
    
    try:
        # Run full analytics pipeline
        state.agent5_analytics.run_full_analytics(batch_id=batch_id)
        
        # Get reports directory
        reports_dir = Path(os.getenv('REPORTS_DIR', 'data/reports'))
        
        return {
            "message": "Analytics report generated successfully",
            "html_dashboard": str(reports_dir / "analytics_dashboard.html"),
            "json_summary": str(reports_dir / "analytics_summary.json"),
            "batch_id": batch_id or "all"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

# ============================================
# Run Application
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    
    print(f"\n🚀 Starting server on {host}:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs\n")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=True
    )
