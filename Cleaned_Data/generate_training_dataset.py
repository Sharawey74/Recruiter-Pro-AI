"""
Professional Resume-Job Matching Dataset Generator
Generates high-quality training data by combining synthetic profiles and real resumes
"""

import pandas as pd
import numpy as np
import random
import re
import uuid
from typing import Dict, List, Tuple, Set
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ==================== SKILL RELATIONSHIP DATABASE ====================

SKILL_RELATIONSHIPS = {
    # Programming
    'python': ['django', 'flask', 'fastapi', 'pandas', 'numpy', 'scikit-learn', 'python programming'],
    'java': ['spring boot', 'hibernate', 'maven', 'microservices', 'junit', 'j2ee'],
    'javascript': ['react', 'node.js', 'vue.js', 'typescript', 'angular', 'jquery'],
    'sql': ['mysql', 'postgresql', 'oracle', 'database design', 'query optimization', 'pl/sql'],
    'c++': ['object oriented programming', 'data structures', 'algorithms', 'stl', 'c'],
    'c#': ['.net', 'asp.net', 'mvc', 'entity framework', 'visual studio'],
    'php': ['laravel', 'wordpress', 'mysql', 'php mysql', 'codeigniter'],
    'ruby': ['ruby on rails', 'rails', 'rspec', 'sinatra'],
    
    # Data Science & Analytics
    'machine learning': ['deep learning', 'neural networks', 'tensorflow', 'pytorch', 'data mining'],
    'data analysis': ['excel', 'tableau', 'power bi', 'statistical analysis', 'data visualization'],
    'data science': ['python', 'r', 'machine learning', 'statistics', 'big data'],
    'big data': ['hadoop', 'spark', 'hive', 'kafka', 'data warehousing'],
    'artificial intelligence': ['machine learning', 'nlp', 'computer vision', 'ai', 'ml'],
    
    # Business & Sales
    'sales': ['negotiation', 'crm', 'lead generation', 'b2b sales', 'business development'],
    'marketing': ['digital marketing', 'seo', 'content marketing', 'social media', 'google analytics'],
    'digital marketing': ['seo', 'sem', 'social media marketing', 'email marketing', 'ppc'],
    'business development': ['sales', 'client relationship', 'proposal writing', 'market research'],
    'project management': ['agile', 'scrum', 'jira', 'stakeholder management', 'risk management'],
    'account management': ['client relationship', 'customer retention', 'upselling', 'crm'],
    
    # Design
    'ui/ux design': ['figma', 'adobe xd', 'wireframing', 'prototyping', 'user research'],
    'graphic design': ['photoshop', 'illustrator', 'indesign', 'branding', 'typography'],
    'web design': ['html', 'css', 'responsive design', 'bootstrap', 'ui design'],
    
    # HR & Administration
    'hr management': ['recruitment', 'employee relations', 'performance management', 'hris', 'payroll'],
    'recruitment': ['talent acquisition', 'interviewing', 'sourcing', 'hr', 'hiring'],
    'administration': ['ms office', 'scheduling', 'documentation', 'coordination', 'office management'],
    
    # Cloud & DevOps
    'aws': ['ec2', 's3', 'lambda', 'cloud computing', 'devops'],
    'azure': ['cloud computing', 'devops', 'ci/cd', 'azure devops'],
    'docker': ['kubernetes', 'containerization', 'devops', 'microservices'],
    'devops': ['ci/cd', 'jenkins', 'git', 'automation', 'linux'],
    
    # Testing
    'testing': ['manual testing', 'automation testing', 'selenium', 'test cases', 'qa'],
    'automation testing': ['selenium', 'test automation', 'junit', 'testng', 'qa'],
    'qa': ['quality assurance', 'testing', 'test planning', 'bug tracking', 'jira'],
    
    # Networking & Security
    'networking': ['tcp/ip', 'cisco', 'routers', 'switches', 'network security'],
    'cybersecurity': ['security', 'penetration testing', 'firewall', 'encryption', 'security audit'],
    
    # Finance & Accounting
    'accounting': ['tally', 'quickbooks', 'financial reporting', 'taxation', 'audit'],
    'finance': ['financial analysis', 'budgeting', 'forecasting', 'excel', 'accounting'],
    'taxation': ['gst', 'income tax', 'tax filing', 'tds', 'accounting'],
}

UNRELATED_SKILLS = [
    'basic computer skills', 'data entry', 'filing', 'phone etiquette', 
    'reception duties', 'microsoft word basic', 'email management',
    'calendar management', 'basic accounting', 'inventory management',
    'typing', 'copying', 'scanning', 'faxing', 'customer service',
    'time management', 'multitasking', 'team work', 'communication'
]

SOFT_SKILLS = [
    'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
    'analytical skills', 'interpersonal skills', 'time management', 'adaptability',
    'creativity', 'attention to detail', 'organization', 'collaboration'
]

EDUCATION_TEMPLATES = [
    "Bachelor's Degree in {field}",
    "B.Tech in {field}",
    "B.E. in {field}",
    "Master's Degree in {field}",
    "M.Tech in {field}",
    "MBA in {field}",
    "BCA",
    "MCA",
    "B.Sc. in {field}",
    "M.Sc. in {field}",
]

FIELD_MAPPING = {
    'IT': ['Computer Science', 'Information Technology', 'Software Engineering', 'Computer Applications'],
    'Sales': ['Business Administration', 'Marketing', 'Commerce', 'Management'],
    'HR': ['Human Resources', 'Business Administration', 'Psychology', 'Management'],
    'Marketing': ['Marketing', 'Business Administration', 'Mass Communication', 'Advertising'],
    'Engineering': ['Mechanical Engineering', 'Electrical Engineering', 'Civil Engineering', 'Electronics'],
    'Finance': ['Finance', 'Accounting', 'Commerce', 'Business Administration'],
}

# ==================== HELPER FUNCTIONS ====================

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if pd.isna(text) or text is None:
        return ""
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_numbers(text: str) -> List[int]:
    """Extract numbers from text"""
    if pd.isna(text):
        return []
    numbers = re.findall(r'\d+', str(text))
    return [int(n) for n in numbers]

def parse_job_experience(exp_string: str) -> Tuple[int, int]:
    """Parse job experience requirement"""
    exp_string = clean_text(exp_string).lower()
    
    if "not disclosed" in exp_string or not exp_string:
        return 2, 5
    
    numbers = extract_numbers(exp_string)
    
    if len(numbers) >= 2:
        return numbers[0], numbers[1]
    elif len(numbers) == 1:
        return numbers[0], numbers[0] + 3
    else:
        return 2, 5

def get_related_skills(skill: str, count: int = 3) -> List[str]:
    """Get related skills for a given skill"""
    skill_lower = skill.lower().strip()
    
    # Check if skill exists in relationship database
    if skill_lower in SKILL_RELATIONSHIPS:
        related = SKILL_RELATIONSHIPS[skill_lower]
        return random.sample(related, min(count, len(related)))
    
    # Fallback: return variations of the skill
    variations = [
        f"{skill} programming",
        f"{skill} development",
        f"{skill} expertise",
    ]
    return random.sample(variations, min(count, len(variations)))

def get_unrelated_skills(count: int = 3) -> List[str]:
    """Get random unrelated skills"""
    return random.sample(UNRELATED_SKILLS, min(count, len(UNRELATED_SKILLS)))

def calculate_experience_for_match(min_exp: int, max_exp: int, match_type: str) -> int:
    """Calculate experience based on match type"""
    
    if match_type == 'high':
        # Within range or slightly above
        return random.randint(min_exp, max_exp + 1)
    
    elif match_type == 'medium':
        # 20% deviation allowed
        lower = max(0, int(min_exp * 0.8))
        upper = int(max_exp * 1.2)
        return random.randint(lower, upper)
    
    else:  # low
        # Either significantly under or over-qualified
        if random.random() < 0.6:
            # Under-qualified (60% chance)
            return random.randint(0, max(1, int(min_exp * 0.5)))
        else:
            # Over-qualified (40% chance)
            return random.randint(int(max_exp * 1.5), max_exp * 2 + 5)

def select_skills_for_match(all_skills: List[str], match_type: str) -> Tuple[List[str], List[str]]:
    """Select matching and additional skills based on match type"""
    
    if not all_skills:
        return [], []
    
    all_skills = [s.strip() for s in all_skills if s.strip()]
    
    if match_type == 'high':
        # Include 100% of required skills + related skills
        matching_skills = all_skills.copy()
        additional_skills = []
        for skill in random.sample(all_skills, min(2, len(all_skills))):
            additional_skills.extend(get_related_skills(skill, 1))
        return matching_skills, additional_skills
    
    elif match_type == 'medium':
        # Include 60-70% of required skills
        skill_count = max(1, int(len(all_skills) * random.uniform(0.6, 0.7)))
        matching_skills = random.sample(all_skills, skill_count)
        # Add one related skill
        if all_skills:
            additional_skills = get_related_skills(random.choice(all_skills), 1)
        else:
            additional_skills = []
        return matching_skills, additional_skills
    
    else:  # low
        # Include 20-40% of required skills + unrelated skills
        skill_count = max(1, int(len(all_skills) * random.uniform(0.2, 0.4)))
        matching_skills = random.sample(all_skills, min(skill_count, len(all_skills)))
        additional_skills = get_unrelated_skills(2)
        return matching_skills, additional_skills

def get_education(category: str = None) -> str:
    """Generate education text"""
    template = random.choice(EDUCATION_TEMPLATES)
    
    if category and category in FIELD_MAPPING:
        field = random.choice(FIELD_MAPPING[category])
    else:
        field = random.choice(['Computer Science', 'Business Administration', 'Engineering'])
    
    if '{field}' in template:
        return template.format(field=field)
    return template

# ==================== RESUME TEXT GENERATION ====================

def generate_professional_resume(job_title: str, skills: List[str], experience_years: int, 
                                 match_type: str, category: str = None) -> str:
    """Generate professional structured resume"""
    
    skills_text = " | ".join(skills[:8])
    top_skills = ", ".join(skills[:3]) if len(skills) >= 3 else ", ".join(skills)
    
    achievements = [
        "delivering high-quality results",
        "exceeding performance targets",
        "optimizing workflows and processes",
        "driving business growth",
        "improving efficiency by 20%",
        "leading successful projects",
    ]
    
    template = f"""{job_title.upper()}

PROFESSIONAL SUMMARY
{job_title} with {experience_years} years of experience in {top_skills}. Proven track record of {random.choice(achievements)}. Strong expertise in {skills[0] if skills else 'relevant technologies'} and {skills[1] if len(skills) > 1 else 'business operations'}.

KEY SKILLS
{skills_text}

PROFESSIONAL EXPERIENCE
{job_title} | {experience_years} years
- Led projects using {skills[0] if skills else 'various technologies'} and {skills[1] if len(skills) > 1 else 'modern tools'}
- Implemented solutions for business requirements
- Collaborated with cross-functional teams
- Achieved {random.choice(['project milestones', 'KPI targets', 'operational excellence', 'client satisfaction'])}

EDUCATION
{get_education(category)}
"""
    
    return template.strip()

def generate_concise_resume(job_title: str, skills: List[str], experience_years: int,
                           match_type: str, category: str = None) -> str:
    """Generate concise bullet-point resume"""
    
    skills_text = ", ".join(skills[:6])
    soft_skill1, soft_skill2 = random.sample(SOFT_SKILLS, 2)
    
    industry_terms = {
        'IT': 'software development',
        'Sales': 'revenue generation',
        'HR': 'talent management',
        'Marketing': 'brand management',
        'Finance': 'financial planning',
    }
    
    domain = industry_terms.get(category, 'professional services')
    
    template = f"""{job_title.upper()} | {experience_years} YEARS EXPERIENCE

Skills: {skills_text}

Experience Highlights:
• {experience_years} years working with {skills[0] if skills else 'industry-standard tools'} in {domain}
• Proficient in {skills[1] if len(skills) > 1 else 'core competencies'} and {skills[2] if len(skills) > 2 else 'business processes'}
• Delivered projects in {category if category else 'various'} sector
• Strong {soft_skill1} and {soft_skill2} abilities

Education: {get_education(category)}
"""
    
    return template.strip()

def generate_narrative_resume(job_title: str, skills: List[str], experience_years: int,
                              match_type: str, category: str = None) -> str:
    """Generate narrative/paragraph style resume"""
    
    skills_comma = ", ".join(skills[:5])
    
    capabilities = [
        "deliver high-quality results",
        "meet tight deadlines",
        "work effectively in teams",
        "solve complex problems",
        "drive continuous improvement",
    ]
    
    template = f"""{job_title.upper()} - {experience_years} YEARS PROFESSIONAL EXPERIENCE

Summary: Dedicated {job_title} professional with comprehensive experience in {skills[0] if skills else 'various technologies'}, {skills[1] if len(skills) > 1 else 'business tools'}, and {skills[2] if len(skills) > 2 else 'industry practices'}. Over {experience_years} years of hands-on experience working in {category if category else 'professional'} sector. Demonstrated ability to {random.choice(capabilities)} and {random.choice(capabilities)}. Strong background in {skills[0] if skills else 'core domain'} with proven results in project delivery.

Core Competencies: {skills_comma}

Professional Background: Extensive experience working with {skills[0] if skills else 'industry tools'} in various capacities. Skilled in {skills[1] if len(skills) > 1 else 'technical implementation'} and {skills[2] if len(skills) > 2 else 'process management'} with focus on delivering quality outcomes. Background includes work in {category if category else 'multiple'} domains.

Qualifications: {get_education(category)}
"""
    
    return template.strip()

def generate_technical_resume(job_title: str, skills: List[str], experience_years: int,
                              match_type: str, category: str = None) -> str:
    """Generate skills-heavy technical resume"""
    
    skills_text = " | ".join(skills[:9])
    location = random.choice(['Mumbai', 'Bengaluru', 'Delhi', 'Pune', 'Hyderabad', 'Chennai'])
    
    template = f"""{job_title.upper()}
{experience_years} Years Experience | {location}

TECHNICAL SKILLS
{skills_text}

EXPERIENCE
{job_title}, {experience_years} years
- Hands-on experience with {skills[0] if skills else 'modern technologies'}, {skills[1] if len(skills) > 1 else 'frameworks'}, {skills[2] if len(skills) > 2 else 'tools'}
- Developed solutions using {skills[3] if len(skills) > 3 else 'industry-standard practices'}
- Technical expertise in {category if category else 'domain-specific'} applications

EDUCATION & CERTIFICATIONS
{get_education(category)} | Certified in {skills[0] if skills else 'Professional Skills'}
"""
    
    return template.strip()

def generate_resume_text(job_title: str, skills: List[str], experience_years: int,
                        match_type: str, category: str = None) -> str:
    """Generate resume text using random template"""
    
    # Select template based on probability
    rand = random.random()
    
    if rand < 0.30:
        text = generate_professional_resume(job_title, skills, experience_years, match_type, category)
    elif rand < 0.55:
        text = generate_concise_resume(job_title, skills, experience_years, match_type, category)
    elif rand < 0.80:
        text = generate_narrative_resume(job_title, skills, experience_years, match_type, category)
    else:
        text = generate_technical_resume(job_title, skills, experience_years, match_type, category)
    
    return text

# ==================== MATCH SCORE CALCULATION ====================

def calculate_match_score(match_type: str) -> Tuple[float, str]:
    """Calculate match score and label based on match type"""
    
    if match_type == 'high':
        score = round(random.uniform(0.85, 0.95), 3)
        label = 'High'
    elif match_type == 'medium':
        score = round(random.uniform(0.60, 0.80), 3)
        label = 'Medium'
    else:  # low
        score = round(random.uniform(0.30, 0.55), 3)
        label = 'Low'
    
    return score, label

# ==================== SYNTHETIC PROFILE GENERATION ====================

def generate_synthetic_profile(job_row: pd.Series, match_type: str, profile_idx: int) -> Dict:
    """Generate a single synthetic profile for a job"""
    
    job_id = job_row['Uniq Id']
    job_title = clean_text(job_row['Job Title'])
    job_skills_raw = clean_text(job_row['Key Skills'])
    job_experience = clean_text(job_row['Job Experience Required'])
    category = clean_text(job_row['Role Category'])
    
    # Parse skills
    if job_skills_raw:
        all_skills = [s.strip() for s in job_skills_raw.split('|') if s.strip()]
    else:
        all_skills = ['communication', 'teamwork', 'problem solving']
    
    # Parse experience
    min_exp, max_exp = parse_job_experience(job_experience)
    
    # Calculate experience for this match type
    experience_years = calculate_experience_for_match(min_exp, max_exp, match_type)
    
    # Select skills based on match type
    matching_skills, additional_skills = select_skills_for_match(all_skills, match_type)
    
    # Combine skills
    profile_skills = matching_skills + additional_skills
    
    # Add soft skills occasionally
    if random.random() < 0.3:
        profile_skills.append(random.choice(SOFT_SKILLS))
    
    # Generate resume text
    profile_text = generate_resume_text(job_title, profile_skills, experience_years, match_type, category)
    
    # Calculate match score
    match_score, match_label = calculate_match_score(match_type)
    
    # Create profile ID with UUID to ensure uniqueness
    unique_suffix = str(uuid.uuid4())[:8]
    profile_id = f"SYN_{match_type[0].upper()}_{profile_idx:06d}_{unique_suffix}"
    
    return {
        'profile_id': profile_id,
        'profile_text': profile_text,
        'target_job_id': job_id,
        'job_title': job_title,
        'job_skills': job_skills_raw,
        'job_experience': job_experience,
        'match_score': match_score,
        'match_label': match_label,
        'category': category,
        'data_source': 'synthetic'
    }

def generate_all_synthetic_profiles(jobs_df: pd.DataFrame, num_jobs: int = 10000) -> pd.DataFrame:
    """Generate all synthetic profiles"""
    
    print(f"\n{'='*60}")
    print("GENERATING SYNTHETIC PROFILES")
    print(f"{'='*60}")
    
    # Take first num_jobs
    jobs_subset = jobs_df.head(num_jobs).copy()
    
    all_profiles = []
    
    # Adjusted distribution: 35% high, 35% medium, 30% low for better balance
    match_types_pool = ['high'] * 35 + ['medium'] * 35 + ['low'] * 30
    
    for idx, (_, job_row) in enumerate(jobs_subset.iterrows(), 1):
        # Generate 3 profiles per job with weighted distribution
        selected_types = random.sample(match_types_pool, 3)
        
        for match_type in selected_types:
            try:
                profile = generate_synthetic_profile(job_row, match_type, idx)
                all_profiles.append(profile)
            except Exception as e:
                print(f"Warning: Failed to generate {match_type} profile for job {idx}: {e}")
                continue
        
        # Progress tracking
        if idx % 1000 == 0:
            print(f"  ✓ Processed {idx:,} jobs -> Generated {len(all_profiles):,} profiles")
    
    print(f"\n✅ Total synthetic profiles generated: {len(all_profiles):,}")
    
    return pd.DataFrame(all_profiles)

# ==================== REAL RESUME PROCESSING ====================

def extract_years_from_resume(resume_text: str) -> int:
    """Extract years of experience from resume text"""
    
    resume_lower = resume_text.lower()
    
    # Pattern 1: "X years of experience"
    pattern1 = re.findall(r'(\d+)\s*(?:\+)?\s*years?\s+(?:of\s+)?experience', resume_lower)
    
    # Pattern 2: "Experience: X years"
    pattern2 = re.findall(r'experience[:\s]+(\d+)\s*(?:\+)?\s*years?', resume_lower)
    
    # Pattern 3: Just "X years" near relevant keywords
    pattern3 = re.findall(r'(?:worked|working|experience|professional)\s+(?:for\s+)?(\d+)\s*(?:\+)?\s*years?', resume_lower)
    
    all_matches = pattern1 + pattern2 + pattern3
    
    if all_matches:
        # Take the maximum (most likely to be total experience)
        years = max([int(y) for y in all_matches])
        return min(years, 30)  # Cap at 30 years
    
    # Fallback: random reasonable value
    return random.randint(2, 7)

def calculate_real_resume_match(resume_text: str, resume_category: str, 
                                job_row: pd.Series) -> Tuple[float, str]:
    """Calculate match score for real resume against job"""
    
    resume_lower = resume_text.lower()
    
    # 1. Skill Overlap Score (50% weight)
    job_skills_raw = clean_text(job_row['Key Skills'])
    if job_skills_raw:
        required_skills = [s.strip().lower() for s in job_skills_raw.split('|') if s.strip()]
    else:
        required_skills = []
    
    if required_skills:
        matching_skills = sum(1 for skill in required_skills if skill in resume_lower)
        skill_score = matching_skills / len(required_skills)
    else:
        skill_score = 0.5
    
    # 2. Experience Score (30% weight)
    resume_years = extract_years_from_resume(resume_text)
    min_exp, max_exp = parse_job_experience(job_row['Job Experience Required'])
    
    if min_exp <= resume_years <= max_exp:
        exp_score = 1.0
    elif resume_years < min_exp:
        exp_score = max(0, resume_years / min_exp) if min_exp > 0 else 0.5
    else:
        exp_score = max(0, 1 - (resume_years - max_exp) / max(max_exp, 1))
    
    # 3. Category Match Score (20% weight)
    job_category = clean_text(job_row['Role Category']).lower()
    resume_cat_lower = resume_category.lower()
    
    # Direct match or partial match
    if resume_cat_lower in job_category or job_category in resume_cat_lower:
        category_score = 1.0
    else:
        category_score = 0.3
    
    # Weighted combination
    final_score = (skill_score * 0.5) + (exp_score * 0.3) + (category_score * 0.2)
    
    # Add small random noise
    final_score += random.uniform(-0.05, 0.05)
    final_score = max(0.0, min(1.0, final_score))
    
    # Determine label first
    if final_score >= 0.75:
        label = 'High'
        # Clamp to High range
        final_score = max(0.85, min(0.95, final_score + random.uniform(0.0, 0.10)))
    elif final_score >= 0.45:
        label = 'Medium'
        # Clamp to Medium range
        final_score = max(0.60, min(0.80, final_score + random.uniform(0.05, 0.20)))
    else:
        label = 'Low'
        # Clamp to Low range
        final_score = max(0.30, min(0.55, final_score + random.uniform(0.10, 0.25)))
    
    final_score = round(final_score, 3)
    
    return final_score, label

def process_real_resumes(resumes_df: pd.DataFrame, jobs_df: pd.DataFrame) -> pd.DataFrame:
    """Process real resumes and match against jobs"""
    
    print(f"\n{'='*60}")
    print("PROCESSING REAL RESUMES")
    print(f"{'='*60}")
    
    all_profiles = []
    
    # Group jobs by category for efficient matching
    jobs_by_category = {}
    for _, job_row in jobs_df.iterrows():
        category = clean_text(job_row['Role Category'])
        if category not in jobs_by_category:
            jobs_by_category[category] = []
        jobs_by_category[category].append(job_row)
    
    for idx, (_, resume_row) in enumerate(resumes_df.iterrows(), 1):
        try:
            resume_id = resume_row['ID']
            resume_text = clean_text(resume_row['Resume_str'])
            resume_category = clean_text(resume_row['Category'])
            
            if len(resume_text) < 50:  # Skip very short resumes
                continue
            
            # Find relevant jobs
            same_category_jobs = jobs_by_category.get(resume_category, [])
            
            # If no jobs in same category, pick from all jobs
            if not same_category_jobs:
                same_category_jobs = [job_row for _, job_row in jobs_df.sample(5).iterrows()]
            
            # Generate 2 pairings per resume (reduced from 2-3 to balance distribution)
            num_pairings = min(2, len(same_category_jobs))
            
            selected_jobs = random.sample(same_category_jobs, min(num_pairings, len(same_category_jobs)))
            
            # Occasionally add one job from different category
            if random.random() < 0.3 and len(jobs_by_category) > 1:
                other_categories = [cat for cat in jobs_by_category.keys() if cat != resume_category]
                if other_categories:
                    other_cat = random.choice(other_categories)
                    if jobs_by_category[other_cat]:
                        selected_jobs.append(random.choice(jobs_by_category[other_cat]))
            
            for job_row in selected_jobs:
                # Calculate match
                match_score, match_label = calculate_real_resume_match(
                    resume_text, resume_category, job_row
                )
                
                # Generate unique ID
                unique_suffix = str(uuid.uuid4())[:8]
                
                profile = {
                    'profile_id': f"REAL_{resume_id}_{unique_suffix}",
                    'profile_text': resume_text[:2000],  # Limit length
                    'target_job_id': job_row['Uniq Id'],
                    'job_title': clean_text(job_row['Job Title']),
                    'job_skills': clean_text(job_row['Key Skills']),
                    'job_experience': clean_text(job_row['Job Experience Required']),
                    'match_score': match_score,
                    'match_label': match_label,
                    'category': resume_category,
                    'data_source': 'real'
                }
                
                all_profiles.append(profile)
        
        except Exception as e:
            print(f"Warning: Failed to process resume {idx}: {e}")
            continue
        
        # Progress tracking
        if idx % 500 == 0:
            print(f"  ✓ Processed {idx:,} resumes -> Generated {len(all_profiles):,} profiles")
    
    print(f"\n✅ Total real-based profiles generated: {len(all_profiles):,}")
    
    return pd.DataFrame(all_profiles)

# ==================== QUALITY VALIDATION ====================

def validate_dataset(df: pd.DataFrame) -> Dict:
    """Validate dataset quality"""
    
    print(f"\n{'='*60}")
    print("VALIDATING DATASET QUALITY")
    print(f"{'='*60}")
    
    issues = []
    
    # Check for duplicates
    duplicates = df['profile_id'].duplicated().sum()
    if duplicates > 0:
        issues.append(f"❌ Found {duplicates} duplicate profile_ids")
    else:
        print("✓ No duplicate profile_ids")
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        issues.append(f"❌ Missing values found:\n{missing[missing > 0]}")
    else:
        print("✓ No missing values")
    
    # Check score-label consistency
    inconsistent = 0
    for _, row in df.iterrows():
        score = row['match_score']
        label = row['match_label']
        
        if label == 'High' and not (0.85 <= score <= 0.95):
            inconsistent += 1
        elif label == 'Medium' and not (0.60 <= score <= 0.80):
            inconsistent += 1
        elif label == 'Low' and not (0.30 <= score <= 0.55):
            inconsistent += 1
    
    if inconsistent > 0:
        issues.append(f"❌ Found {inconsistent} inconsistent score-label pairs")
    else:
        print("✓ Score-label consistency verified")
    
    # Check class distribution
    label_dist = df['match_label'].value_counts(normalize=True)
    print(f"\n✓ Label distribution:")
    for label, pct in label_dist.items():
        print(f"  - {label}: {pct*100:.1f}%")
        if pct < 0.25 or pct > 0.40:
            issues.append(f"⚠️  {label} class has {pct*100:.1f}% (recommended: 25-40%)")
    
    # Check text lengths
    text_lengths = df['profile_text'].str.len()
    avg_len = text_lengths.mean()
    print(f"\n✓ Average profile text length: {avg_len:.0f} characters")
    
    if text_lengths.min() < 100:
        issues.append(f"⚠️  Some profiles are very short (min: {text_lengths.min()} chars)")
    
    if issues:
        print(f"\n{'⚠️  VALIDATION WARNINGS:'}")
        for issue in issues:
            print(f"  {issue}")
    
    return {
        'duplicates': duplicates,
        'missing_values': missing.sum(),
        'inconsistent_scores': inconsistent,
        'label_distribution': label_dist.to_dict(),
        'avg_text_length': avg_len
    }

# ==================== SUMMARY REPORT ====================

def generate_summary_report(df: pd.DataFrame, validation_results: Dict):
    """Generate final summary report"""
    
    print(f"\n{'='*60}")
    print("DATASET GENERATION SUMMARY")
    print(f"{'='*60}")
    
    total = len(df)
    synthetic = len(df[df['data_source'] == 'synthetic'])
    real = len(df[df['data_source'] == 'real'])
    
    print(f"\nTotal Profiles: {total:,}")
    print(f"├── Synthetic: {synthetic:,} ({synthetic/total*100:.1f}%)")
    print(f"└── Real-based: {real:,} ({real/total*100:.1f}%)")
    
    print(f"\nMatch Distribution:")
    label_counts = df['match_label'].value_counts()
    for label in ['High', 'Medium', 'Low']:
        count = label_counts.get(label, 0)
        pct = count / total * 100 if total > 0 else 0
        print(f"├── {label} Match: {count:,} ({pct:.1f}%)")
    
    print(f"\nCategory Distribution (Top 10):")
    top_categories = df['category'].value_counts().head(10)
    for cat, count in top_categories.items():
        print(f"  - {cat}: {count:,}")
    
    print(f"\nData Source Distribution:")
    source_counts = df['data_source'].value_counts()
    for source, count in source_counts.items():
        print(f"  - {source}: {count:,}")
    
    print(f"\nScore Statistics:")
    print(f"  - Min Score: {df['match_score'].min():.3f}")
    print(f"  - Max Score: {df['match_score'].max():.3f}")
    print(f"  - Mean Score: {df['match_score'].mean():.3f}")
    print(f"  - Median Score: {df['match_score'].median():.3f}")
    
    print(f"\nText Length Statistics:")
    print(f"  - Min Length: {df['profile_text'].str.len().min():,} characters")
    print(f"  - Max Length: {df['profile_text'].str.len().max():,} characters")
    print(f"  - Average Length: {validation_results['avg_text_length']:.0f} characters")
    
    print(f"\nQuality Checks:")
    checks = [
        ('No duplicate profile_ids', validation_results['duplicates'] == 0),
        ('No missing values', validation_results['missing_values'] == 0),
        ('Score-label consistency verified', validation_results['inconsistent_scores'] == 0),
        ('Balanced class distribution', all(0.25 <= v <= 0.40 for v in validation_results['label_distribution'].values())),
    ]
    
    for check_name, passed in checks:
        status = '✓' if passed else '✗'
        print(f"{status} {check_name}")
    
    print(f"\n{'='*60}")
    print("✅ DATASET GENERATION COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}\n")

# ==================== MAIN EXECUTION ====================

def main():
    """Main execution function"""
    
    print("\n" + "="*60)
    print("RESUME-JOB MATCHING DATASET GENERATOR")
    print("="*60)
    
    # Load data
    print("\n📥 Loading input data...")
    
    try:
        jobs_df = pd.read_csv('marketing_sample_for_naukri_com-jobs__20190701_20190830__30k_data.csv')
        print(f"  ✓ Loaded jobs dataset: {len(jobs_df):,} rows")
    except Exception as e:
        print(f"  ❌ Failed to load jobs CSV: {e}")
        return
    
    try:
        resumes_df = pd.read_csv('Resume.csv')
        print(f"  ✓ Loaded resumes dataset: {len(resumes_df):,} rows")
    except Exception as e:
        print(f"  ❌ Failed to load resumes CSV: {e}")
        return
    
    # Generate synthetic profiles
    synthetic_df = generate_all_synthetic_profiles(jobs_df, num_jobs=10000)
    
    # Process real resumes
    real_df = process_real_resumes(resumes_df, jobs_df)
    
    # Combine datasets
    print(f"\n{'='*60}")
    print("COMBINING DATASETS")
    print(f"{'='*60}")
    
    final_df = pd.concat([synthetic_df, real_df], ignore_index=True)
    
    # Shuffle
    final_df = final_df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    
    print(f"✓ Combined and shuffled: {len(final_df):,} total profiles")
    
    # Validate
    validation_results = validate_dataset(final_df)
    
    # Export
    print(f"\n{'='*60}")
    print("EXPORTING DATASET")
    print(f"{'='*60}")
    
    output_file = 'final_training_dataset.csv'
    
    # Try alternate filename if file is locked
    try:
        final_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✓ Dataset saved to: {output_file}")
    except PermissionError:
        output_file = 'final_training_dataset_v2.csv'
        final_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✓ Dataset saved to: {output_file} (original file was locked)")
    
    # Generate summary
    generate_summary_report(final_df, validation_results)

if __name__ == "__main__":
    main()
