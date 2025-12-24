"""
Unified Backend for Direct Mode
Allows running the application without a separate API server.
"""
import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import project modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.agent1_parser import RawParser
from src.agents.agent2 import CandidateExtractor
from src.agents.agent3 import JobMatcher

class HRBackend:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HRBackend, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def initialize(self):
        """Initialize all agents if not already initialized."""
        if self.initialized:
            return

        print("\n=== Initializing 3-Agent Pipeline ===")
        
        # Initialize 3 Agents (Rule-Based, No APIs, No Ollama)
        self.agent1 = RawParser()
        self.agent2 = CandidateExtractor()
        self.agent3 = JobMatcher()
        
        print("  ✓ Agent 1: File Parser (PDF/DOCX/TXT)")
        print("  ✓ Agent 2: Candidate Extractor (Regex + Dictionary)")
        print("  ✓ Agent 3: Job Matcher & Decision Engine (Rule-Based)")
        
        # Load Jobs (canonical - exactly 3 jobs)
        self.jobs_data = self._load_jobs()
        
        self.initialized = True
        print(f"  ✓ Backend Ready: {len(self.jobs_data)} jobs loaded")
        print("="*50)

    def _load_jobs(self) -> List[Dict]:
        """Load jobs from jobs.json with configurable limit."""
        # Get job limit from environment or use default
        job_limit = int(os.getenv('MAX_JOBS', '5000'))  # Default: 5000 jobs
        
        jobs_path = Path('data/json/jobs.json')
        if jobs_path.exists():
            with open(jobs_path, 'r', encoding='utf-8') as f:
                all_jobs = json.load(f)
            
            # Take first N jobs (or all if limit is 0)
            raw_jobs = all_jobs[:job_limit] if job_limit > 0 else all_jobs
            
            # Normalize to expected format
            jobs = self._normalize_jobs(raw_jobs)
            print(f"Loaded {len(jobs)} jobs from jobs.json (total available: {len(all_jobs)})")
            return jobs
        
        # Fallback to canonical
        canonical_path = Path('data/json/jobs_canonical.json')
        if canonical_path.exists():
            with open(canonical_path, 'r', encoding='utf-8') as f:
                jobs = json.load(f)
            print(f"WARNING: Using fallback canonical jobs ({len(jobs)} jobs)")
            return jobs
        
        return []
    
    def _normalize_jobs(self, raw_jobs: List[Dict]) -> List[Dict]:
        """Normalize jobs.json format to expected format."""
        normalized = []
        
        for job in raw_jobs:
            # Extract experience years from string like "1 - 2 yrs" or "2 - 5 yrs"
            exp_str = job.get('Experience', '0')
            min_exp = 0
            if exp_str and '-' in exp_str:
                parts = exp_str.split('-')
                try:
                    min_exp = int(parts[0].strip())
                except:
                    min_exp = 0
            
            # Parse skills from pipe-separated string
            skills_str = job.get('skills', '')
            skills = [s.strip().lower() for s in skills_str.split('|') if s.strip()]
            
            normalized_job = {
                'job_id': job.get('Job Id', ''),
                'title': job.get('Job Title', ''),
                'description': job.get('Qualifications', ''),
                'required_skills': skills,
                'min_experience_years': min_exp,
                'location': job.get('Location', ''),
                'employment_type': 'Full-time',  # Default
                'posted_date': ''  # Not available in jobs.json
            }
            normalized.append(normalized_job)
        
        return normalized

    def get_jobs(self, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get jobs list with optional filtering."""
        if not self.initialized: self.initialize()
        jobs = self.jobs_data[:limit] if limit > 0 else self.jobs_data
        return jobs

    def process_match(self, profile_text: str, top_k: int = 3) -> Dict:
        """Process full matching pipeline using 3-agent system.
        
        Args:
            profile_text: Raw resume text
            top_k: Number of top matches (max 3)
        """
        if not self.initialized: self.initialize()
        
        start_time = datetime.now()
        profile_id = f"profile_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        print("\n⚡ Processing resume through 3-agent pipeline...")
        
        # Step 1: Extract candidate data (Agent 2)
        candidate_profile = self.agent2.extract(profile_text)
        print(f"  Agent 2: Extracted {len(candidate_profile['skills'])} skills")
        
        # Step 2: Match and decide (Agent 3)
        match_results = self.agent3.match_and_decide(candidate_profile, self.jobs_data)
        print(f"  Agent 3: Matched against {len(self.jobs_data)} jobs")
        
        # 3. Format Output for UI
        top_matches = []
        for match in match_results[:top_k]:
            # Find full job data
            job_data = next((j for j in self.jobs_data if j['job_id'] == match['job_id']), {})
            
            top_matches.append({
                "job_id": match['job_id'],
                "job_title": match['job_title'],
                "match_label": self._score_to_label(match['score']),  # High/Medium/Low
                "confidence": match['score'] / 100.0,
                "decision": match['decision'],  # SHORTLIST/REVIEW/REJECT
                "explanation": match['explanation'],  # Detailed explanation
                "skill_match": {
                    "matched_skills": match['matched_skills'],
                    "missing_skills": match['missing_skills'],
                    "skill_match_score": match['skill_match_percentage'] / 100.0
                },
                "experience_match_score": 1.0 if match['experience_match'] else 0.5,
                "warnings": [],
                "ranking": match['ranking'],
                "breakdown": match['breakdown']
            })
            
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "profile_id": profile_id,
            "candidate_name": candidate_profile.get("name", "Unknown Candidate"),
            "total_jobs_scored": len(self.jobs_data),
            "top_matches": top_matches,
            "processing_time_seconds": processing_time,
            "extraction_details": {
                "email": candidate_profile.get("email", ""),
                "phone": candidate_profile.get("phone", ""),
                "skills_count": len(candidate_profile.get("skills", [])),
                "experience_years": candidate_profile.get("experience_years", 0),
                "confidence": candidate_profile.get("extraction_confidence", 0.0)
            }
        }
    
    def _score_to_label(self, score: float) -> str:
        """Convert numeric score to High/Medium/Low label"""
        if score >= 70:
            return "High"
        elif score >= 40:
            return "Medium"
        else:
            return "Low"

    def get_analytics(self, type: str = "metrics", batch_id: str = None) -> Dict:
        """Analytics disabled - no LLM dependencies"""
        return {
            "message": "Analytics feature removed (no Ollama/LLM dependencies)",
            "suggestion": "Use basic statistics from match results instead"
        }

# Singleton instance
backend = HRBackend()
