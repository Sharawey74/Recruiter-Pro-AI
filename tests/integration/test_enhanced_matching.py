"""
Test Enhanced Agent 3 Matching
Compare old vs new scoring for Abdelrahman's resume
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.agent1_parser import RawParser
from src.agents.agent2_extractor import CandidateExtractor
from src.agents.agent3_scorer import HybridScoringAgent
from src.storage.models import CVProfile, JobPosting
import json
import uuid

def test_enhanced_matching():
    print("\n" + "="*100)
    print("TESTING ENHANCED AGENT 3 MATCHING")
    print("="*100)
    
    # Load Abdelrahman's resume
    resume_path = "test_resume_abdelrahman.txt"
    
    # Parse CV
    parser = RawParser()
    extractor = CandidateExtractor()
    scorer = HybridScoringAgent()
    
    print(f"\n📄 Parsing resume: {resume_path}")
    result = parser.parse_file(resume_path)
    cv_text = result.get('raw_text', '')
    
    print("🔍 Extracting candidate data...")
    extracted = extractor.extract(cv_text)
    
    # Build CV profile
    cv = CVProfile(
        cv_id=str(uuid.uuid4()),
        file_name=resume_path,
        file_path=resume_path,
        name=extracted.get('name', 'Abdelrahman Mohamed'),
        email=extracted.get('email'),
        skills=extracted.get('skills', []),
        experience_years=extracted.get('experience_years', 3),
        education=', '.join(extracted.get('education', [])) if isinstance(extracted.get('education'), list) else extracted.get('education', 'Bachelor'),
        raw_text=cv_text,
        extracted_data=extracted
    )
    
    print(f"\n✅ Candidate Profile:")
    print(f"   Name: {cv.name}")
    print(f"   Experience: {cv.experience_years} years")
    print(f"   Skills ({len(cv.skills)}): {', '.join(cv.skills[:15])}{'...' if len(cv.skills) > 15 else ''}")
    
    # Load jobs
    print(f"\n📦 Loading jobs from data/json/jobs_cleaned.json...")
    with open('data/json/jobs_cleaned.json', 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)
    
    jobs = [JobPosting(**j) for j in jobs_data[:4000]]
    print(f"✅ Loaded {len(jobs)} jobs")
    
    # Score against all jobs
    print(f"\n⚡ Scoring candidate against {len(jobs)} jobs...")
    matches = []
    
    for i, job in enumerate(jobs):
        if (i + 1) % 1000 == 0:
            print(f"   Processed {i+1}/{len(jobs)}...")
        
        score = scorer.score_match(cv, job, include_ml=False)
        matches.append({
            'job': job,
            'score': score
        })
    
    # Sort by hybrid score
    matches.sort(key=lambda x: x['score'].hybrid_score, reverse=True)
    
    # Display top 15 matches
    print(f"\n" + "="*100)
    print("TOP 15 MATCHED JOBS")
    print("="*100)
    
    for i, match in enumerate(matches[:15], 1):
        job = match['job']
        score = match['score']
        
        print(f"\n{i}. {job.title}")
        print(f"   Company: {job.company_name}")
        print(f"   Location: {job.location_city}, {job.location_country} ({job.remote_type})")
        print(f"   Seniority: {job.seniority_level} | Experience: {job.min_experience_years}-{job.max_experience_years} years")
        print(f"   📊 SCORES:")
        print(f"      • Overall Score: {score.hybrid_score*100:.1f}%")
        print(f"      • Skills Match: {score.skill_score*100:.1f}% ({len(score.matched_skills)}/{len(job.required_skills)} required)")
        print(f"      • Title Match: {score.hybrid_score*100 - (score.skill_score*50 + score.experience_score*20 + score.education_score*8 + score.keyword_score*5):.1f}% (NEW!)")
        print(f"      • Experience: {score.experience_score*100:.1f}%")
        print(f"      • Education: {score.education_score*100:.1f}%")
        print(f"   ✅ Matched Skills: {', '.join(score.matched_skills[:8])}{'...' if len(score.matched_skills) > 8 else ''}")
        if score.missing_skills:
            print(f"   ⚠️  Missing Skills: {', '.join(score.missing_skills[:5])}{'...' if len(score.missing_skills) > 5 else ''}")
    
    # Statistics
    print(f"\n" + "="*100)
    print("MATCHING STATISTICS")
    print("="*100)
    
    excellent = sum(1 for m in matches if m['score'].hybrid_score >= 0.75)
    good = sum(1 for m in matches if 0.60 <= m['score'].hybrid_score < 0.75)
    moderate = sum(1 for m in matches if 0.50 <= m['score'].hybrid_score < 0.60)
    poor = sum(1 for m in matches if m['score'].hybrid_score < 0.50)
    
    print(f"Excellent matches (≥75%): {excellent} ({excellent/len(matches)*100:.1f}%)")
    print(f"Good matches (60-74%): {good} ({good/len(matches)*100:.1f}%)")
    print(f"Moderate matches (50-59%): {moderate} ({moderate/len(matches)*100:.1f}%)")
    print(f"Poor matches (<50%): {poor} ({poor/len(matches)*100:.1f}%)")
    
    print(f"\n✨ Enhanced matching complete!")

if __name__ == "__main__":
    test_enhanced_matching()
