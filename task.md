# 🎯 Stage-by-Stage Implementation Plan

**Project:** Resume-Job Matching Multi-Agent System  
**Approach:** Incremental development with testing at each stage  
**Timeline:** 10 days (1-2 days per stage)  

---

## 📋 STAGE 1: Data & Parsers (Days 1-2)

### Goal
Implement Agent 1 (Profile & Job Parser) with dual-mode parsing capability.

### Tasks

#### 1.1 Setup Project Structure
- [ ] Create all required directories (`data/json/`, `models/`, `src/agents/`, etc.)
- [ ] Verify `requirements.txt` is correct
- [ ] Install all dependencies: `pip install -r requirements.txt`
- [ ] Download spaCy model: `python -m spacy download en_core_web_sm`
- [ ] Test imports work correctly

#### 1.2 Prepare Training Data
- [ ] Verify `final_training_dataset_v2.csv` is in `data/raw/`
- [ ] Run: `python scripts/prepare_jobs_json.py`
- [ ] Verify `data/json/jobs.json` created (100 jobs)
- [ ] Verify `data/json/resumes_sample.json` created (15 samples)
- [ ] Inspect JSON files to ensure correct format

#### 1.3 Implement Agent 1 - Profile Parser
- [ ] Create `src/agents/__init__.py`
- [ ] Create `src/agents/agent1_parser.py`
- [ ] Implement `ProfileJobParser` class
- [ ] Implement `parse_profile()` method
  - [ ] Text cleaning
  - [ ] Skill extraction (regex + spaCy)
  - [ ] Experience extraction
  - [ ] Education extraction
  - [ ] Job title extraction
  - [ ] Seniority determination
- [ ] Implement spaCy + NLTK fallback mechanism
- [ ] Implement `_save_parsed_profile()` to save JSON

#### 1.4 Implement Agent 1 - Job Parser
- [ ] Implement `parse_job()` method
- [ ] Parse pipe-separated skills
- [ ] Parse experience range (e.g., "5 - 10 yrs")
- [ ] Clean job description text
- [ ] Return structured job JSON

#### 1.5 Create Utility Functions
- [ ] Create `src/utils/__init__.py`
- [ ] Create `src/utils/text_processing.py`
  - [ ] `clean_text()` function
  - [ ] `remove_stopwords()` function
- [ ] Create `src/utils/skill_extraction.py`
  - [ ] Skill pattern definitions
  - [ ] Skill matching functions

#### 1.6 Unit Testing
- [ ] Create `tests/__init__.py`
- [ ] Create `tests/test_agent1_parser.py`
- [ ] Test skill extraction with sample text
- [ ] Test experience extraction with various formats
- [ ] Test education extraction
- [ ] Test spaCy fallback to NLTK
- [ ] Test profile parsing end-to-end
- [ ] Test job parsing end-to-end
- [ ] Run: `pytest tests/test_agent1_parser.py -v`
- [ ] Ensure all tests pass

#### 1.7 Manual Testing
- [ ] Test with sample resume from `resumes_sample.json`
- [ ] Verify parsed profile saved to `data/json/parsed_profiles/`
- [ ] Inspect output JSON for correctness
- [ ] Test with at least 3 different resume styles

### Success Criteria
✅ Agent 1 can parse profiles and jobs  
✅ Outputs valid JSON files  
✅ All unit tests pass  
✅ spaCy + NLTK fallback works  

### Deliverables
- `src/agents/agent1_parser.py` (complete)
- `src/utils/text_processing.py`
- `src/utils/skill_extraction.py`
- `tests/test_agent1_parser.py`
- Sample parsed profiles in `data/json/parsed_profiles/`

---

## 📋 STAGE 2: Feature Engineering (Days 3-4)

### Goal
Implement Agent 2 (Feature Generator) to compute matching features.

### Tasks

#### 2.1 Implement Agent 2 - Feature Generator
- [ ] Create `src/agents/agent2_features.py`
- [ ] Implement `FeatureGenerator` class
- [ ] Load or create TF-IDF vectorizer

#### 2.2 Implement Feature Calculation Methods
- [ ] Implement `generate_features()` method
- [ ] **Skill Overlap Features:**
  - [ ] `skill_overlap_count`
  - [ ] `skill_overlap_ratio`
  - [ ] `jaccard_similarity`
  - [ ] `profile_skill_count`
  - [ ] `job_skill_count`
- [ ] **Experience Features:**
  - [ ] `experience_delta`
  - [ ] `experience_match` (binary)
  - [ ] `overqualified` (binary)
  - [ ] `underqualified` (binary)
  - [ ] `experience_ratio`
- [ ] **Category Features:**
  - [ ] `category_exact_match`
  - [ ] `category_partial_match`
- [ ] **Text Similarity:**
  - [ ] `tfidf_similarity` (cosine similarity)
- [ ] **Other Features:**
  - [ ] `seniority_match`
  - [ ] `profile_word_count`
  - [ ] `has_education`

#### 2.3 Implement Feature Vector Generation
- [ ] Implement `generate_feature_vector()` method
- [ ] Define feature order (12 features)
- [ ] Convert feature dict to numpy array
- [ ] Handle missing values (default to 0.0)

#### 2.4 Implement Feature Persistence
- [ ] Implement `save_features()` method
- [ ] Save to `data/json/features/{profile_id}_{job_id}.json`
- [ ] Create directory if doesn't exist

#### 2.5 Unit Testing
- [ ] Create `tests/test_agent2_features.py`
- [ ] Test skill overlap calculations
- [ ] Test experience delta calculations
- [ ] Test category matching
- [ ] Test TF-IDF similarity
- [ ] Test feature vector generation
- [ ] Test with edge cases (empty skills, missing data)
- [ ] Run: `pytest tests/test_agent2_features.py -v`

#### 2.6 Integration Testing
- [ ] Load parsed profile from Stage 1
- [ ] Load job from `jobs.json`
- [ ] Generate features
- [ ] Verify feature values are reasonable
- [ ] Test with 5+ profile-job pairs

### Success Criteria
✅ Agent 2 generates 12 features correctly  
✅ Features are numerical and normalized  
✅ All unit tests pass  
✅ Integration with Agent 1 works  

### Deliverables
- `src/agents/agent2_features.py` (complete)
- `tests/test_agent2_features.py`
- Sample features in `data/json/features/`

---

## 📋 STAGE 3: ML Model Training (Days 4-6)

### Goal
Train classifier model and implement Agent 2.5 (ML Scorer).

### Tasks

#### 3.1 Train Classification Model
- [ ] Verify `data/raw/final_training_dataset_v2.csv` exists
- [ ] Run: `python scripts/train_models.py`
- [ ] Monitor training output
- [ ] Verify models saved to `models/`:
  - [ ] `classifier.pkl`
  - [ ] `tfidf_vectorizer.pkl`
  - [ ] `label_encoder.pkl`
  - [ ] `model_metadata.json`
- [ ] Check validation accuracy (target: >75%)
- [ ] Review classification report

#### 3.2 Verify Agent 2.5 Implementation
- [ ] Review `src/agents/agent2_5_scorer.py` (already created)
- [ ] Verify `HybridMLScorer` class exists
- [ ] Verify rule-based smoothing logic

#### 3.3 Test Agent 2.5
- [ ] Run: `python src/agents/agent2_5_scorer.py`
- [ ] Verify models load successfully
- [ ] Test with dummy feature vector
- [ ] Verify output format:
  - [ ] `predicted_label` (High/Medium/Low)
  - [ ] `predicted_score` (0.0-1.0)
  - [ ] `class_probabilities` (dict)
  - [ ] `confidence` (0.0-1.0)
  - [ ] `smoothing_flags` (list)

#### 3.4 Implement Rule-Based Smoothing
- [ ] Review smoothing rules in Agent 2.5
- [ ] Test high confidence enforcement (prob > 0.85)
- [ ] Test downgrade from High (prob < 0.60)
- [ ] Test downgrade from Medium (prob < 0.35)
- [ ] Test ambiguous prediction detection

#### 3.5 Unit Testing
- [ ] Create `tests/test_agent2_5_scorer.py`
- [ ] Test model loading
- [ ] Test prediction with sample features
- [ ] Test smoothing rules
- [ ] Test confidence calculation
- [ ] Test context-aware rules (if implemented)
- [ ] Run: `pytest tests/test_agent2_5_scorer.py -v`

#### 3.6 End-to-End Testing
- [ ] Load parsed profile (Agent 1 output)
- [ ] Load job
- [ ] Generate features (Agent 2)
- [ ] Predict match (Agent 2.5)
- [ ] Verify complete pipeline works
- [ ] Test with 10+ profile-job pairs

### Success Criteria
✅ Model trained with >75% accuracy  
✅ Agent 2.5 predicts correctly  
✅ Rule smoothing works as expected  
✅ All unit tests pass  
✅ End-to-end pipeline functional  

### Deliverables
- `models/classifier.pkl`
- `models/tfidf_vectorizer.pkl`
- `models/label_encoder.pkl`
- `models/model_metadata.json`
- `tests/test_agent2_5_scorer.py`

---

## 📋 STAGE 4: Ranking & Explainability (Day 6)

### Goal
Implement Agent 3 (Decision & Explanation Engine).

### Tasks

#### 4.1 Create Configuration Files
- [ ] Create `config/` directory
- [ ] Create `config/rules.yaml`
  - [ ] Define decision thresholds
  - [ ] Define business rules
  - [ ] Define actions for each decision
- [ ] Create `config/thresholds.yaml`
  - [ ] Shortlist threshold (0.85)
  - [ ] Review threshold (0.60)
  - [ ] Reject threshold (<0.60)

#### 4.2 Implement Agent 3 - Decision Engine
- [ ] Create `src/agents/agent3_ranker.py`
- [ ] Implement `DecisionEngine` class
- [ ] Implement `load_rules()` method
- [ ] Implement `make_decision()` method

#### 4.3 Implement Decision Logic
- [ ] Apply score-based thresholds
- [ ] Apply business rules:
  - [ ] Minimum experience check
  - [ ] Critical skill missing check
  - [ ] Overqualified check
- [ ] Combine ML score + rules
- [ ] Generate final decision (SHORTLIST/REVIEW/REJECT)

#### 4.4 Implement Explanation Generation
- [ ] Implement `generate_explanation()` method
- [ ] List matched skills
- [ ] List missing skills
- [ ] Explain score reasoning
- [ ] Explain rule triggers
- [ ] Format as human-readable text

#### 4.5 Implement Ranking
- [ ] Implement `rank_matches()` method
- [ ] Sort by final score (descending)
- [ ] Apply tie-breaking rules
- [ ] Return top N matches

#### 4.6 Implement Result Persistence
- [ ] Implement `save_decision()` method
- [ ] Save to `data/json/results/{profile_id}_results.json`
- [ ] Include:
  - [ ] Profile ID
  - [ ] Job matches (ranked)
  - [ ] Scores and labels
  - [ ] Explanations
  - [ ] Timestamp

#### 4.7 Unit Testing
- [ ] Create `tests/test_agent3_ranker.py`
- [ ] Test decision logic
- [ ] Test business rules
- [ ] Test explanation generation
- [ ] Test ranking algorithm
- [ ] Run: `pytest tests/test_agent3_ranker.py -v`

#### 4.8 Integration Testing
- [ ] Test full pipeline: Agent 1 → 2 → 2.5 → 3
- [ ] Verify decisions are consistent
- [ ] Verify explanations are clear
- [ ] Test with 10+ profiles

### Success Criteria
✅ Agent 3 makes consistent decisions  
✅ Explanations are clear and accurate  
✅ Ranking works correctly  
✅ All unit tests pass  

### Deliverables
- `config/rules.yaml`
- `config/thresholds.yaml`
- `src/agents/agent3_ranker.py`
- `tests/test_agent3_ranker.py`
- Sample results in `data/json/results/`

---

## 📋 STAGE 5: FastAPI Gateway (Day 7)

### Goal
Create FastAPI application to connect all agents.

### Tasks

#### 5.1 Implement FastAPI Application
- [ ] Create `src/api.py`
- [ ] Import FastAPI and dependencies
- [ ] Create FastAPI app instance
- [ ] Configure CORS if needed

#### 5.2 Implement Data Models (Pydantic)
- [ ] Create `ProfileInput` model
- [ ] Create `JobInput` model
- [ ] Create `MatchRequest` model
- [ ] Create `MatchResponse` model

#### 5.3 Implement Endpoints

**POST /match**
- [ ] Accept profile text
- [ ] Optional: accept job preferences
- [ ] Call Agent 1 to parse profile
- [ ] Load jobs from `jobs.json`
- [ ] For each job:
  - [ ] Call Agent 2 to generate features
  - [ ] Call Agent 2.5 to predict match
- [ ] Call Agent 3 to rank and decide
- [ ] Return top N matches with explanations

**GET /jobs**
- [ ] Load `data/json/jobs.json`
- [ ] Return all available jobs
- [ ] Optional: filter by category

**GET /health**
- [ ] Check if models loaded
- [ ] Return system status

**POST /upload-profile**
- [ ] Accept file upload
- [ ] Save to temp location
- [ ] Parse with Agent 1
- [ ] Return parsed profile

#### 5.4 Implement Helper Functions
- [ ] `load_jobs()` - Load jobs from JSON
- [ ] `load_models()` - Load ML models on startup
- [ ] `process_match()` - Core matching logic

#### 5.5 Add Error Handling
- [ ] Try-except blocks for all endpoints
- [ ] Return proper HTTP status codes
- [ ] Return error messages in JSON format

#### 5.6 Testing

**Manual Testing:**
- [ ] Start server: `uvicorn src.api:app --reload`
- [ ] Open: http://localhost:8000/docs
- [ ] Test `/health` endpoint
- [ ] Test `/jobs` endpoint
- [ ] Test `/match` endpoint with sample profile
- [ ] Verify response format

**API Testing:**
- [ ] Test with curl commands
- [ ] Test with Python requests
- [ ] Test error cases (invalid input)

### Success Criteria
✅ FastAPI server starts without errors  
✅ All endpoints work correctly  
✅ Swagger docs accessible  
✅ Returns proper JSON responses  

### Deliverables
- `src/api.py` (complete)
- API documentation (auto-generated)

---

## 📋 STAGE 6: Streamlit UI (Days 8-9)

### Goal
Create user-friendly Streamlit interface for HR users.

### Tasks

#### 6.1 Setup Streamlit Structure
- [ ] Create `streamlit_app/` directory
- [ ] Create `streamlit_app/app.py` (main app)
- [ ] Create `streamlit_app/pages/` directory
- [ ] Create `streamlit_app/components/` directory

#### 6.2 Implement Main App
- [ ] Create `streamlit_app/app.py`
- [ ] Set page config (title, icon, layout)
- [ ] Create sidebar navigation
- [ ] Add home page content

#### 6.3 Implement Page 1: Upload CV
- [ ] Create `streamlit_app/pages/1_upload_cv.py`
- [ ] Add CV upload widget (file or text area)
- [ ] Add "Parse CV" button
- [ ] Call FastAPI `/upload-profile` endpoint
- [ ] Display parsed profile (skills, experience, etc.)
- [ ] Add "Find Matches" button

#### 6.4 Implement Page 2: Match Results
- [ ] Create `streamlit_app/pages/2_match_results.py`
- [ ] Call FastAPI `/match` endpoint
- [ ] Display top N matches
- [ ] For each match show:
  - [ ] Job title
  - [ ] Match score (with color coding)
  - [ ] Match label (High/Medium/Low)
  - [ ] Matched skills (green badges)
  - [ ] Missing skills (red badges)
  - [ ] Explanation text
- [ ] Add download results button (JSON)

#### 6.5 Implement Page 3: Analytics Dashboard
- [ ] Create `streamlit_app/pages/3_analytics.py`
- [ ] Load prediction logs
- [ ] Display metrics:
  - [ ] Total profiles processed
  - [ ] Match distribution (pie chart)
  - [ ] Average confidence score
- [ ] Add visualizations with Plotly

#### 6.6 Implement Page 4: Job Management
- [ ] Create `streamlit_app/pages/4_job_management.py`
- [ ] Display all jobs from `jobs.json`
- [ ] Add search/filter functionality
- [ ] Show job details on click

#### 6.7 Create Reusable Components
- [ ] Create `streamlit_app/components/cv_uploader.py`
- [ ] Create `streamlit_app/components/job_selector.py`
- [ ] Create `streamlit_app/components/results_display.py`

#### 6.8 Add Styling
- [ ] Create custom CSS for better UI
- [ ] Add color coding for match levels
- [ ] Add icons and emojis
- [ ] Ensure responsive design

#### 6.9 Testing

**Local Testing:**
- [ ] Run: `streamlit run streamlit_app/app.py`
- [ ] Test CV upload (file and text)
- [ ] Test profile parsing
- [ ] Test match results display
- [ ] Test all navigation pages
- [ ] Test on different screen sizes

**Integration Testing:**
- [ ] Ensure FastAPI is running
- [ ] Test end-to-end flow
- [ ] Test with multiple profiles
- [ ] Test error handling

#### 6.10 Prepare for Deployment
- [ ] Create `.streamlit/config.toml` (optional)
- [ ] Test with sample data
- [ ] Document deployment steps

### Success Criteria
✅ Streamlit UI loads without errors  
✅ All pages functional  
✅ CV upload and matching works  
✅ Results display correctly  
✅ Ready for Streamlit Cloud deployment  

### Deliverables
- `streamlit_app/app.py`
- `streamlit_app/pages/` (4 pages)
- `streamlit_app/components/` (3 components)

---

## 📋 STAGE 7: Testing & Documentation (Day 10)

### Goal
Complete testing, documentation, and prepare demo.

### Tasks

#### 7.1 Complete Unit Tests
- [ ] Ensure all agents have tests
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Achieve >80% code coverage
- [ ] Fix any failing tests

#### 7.2 Integration Testing
- [ ] Test complete pipeline end-to-end
- [ ] Test with 20+ different profiles
- [ ] Test edge cases
- [ ] Document any issues found

#### 7.3 Update Documentation
- [ ] Update `README.md` with final instructions
- [ ] Add screenshots to README
- [ ] Document API endpoints
- [ ] Add troubleshooting section

#### 7.4 Create Demo Materials
- [ ] Prepare demo script
- [ ] Create sample test cases
- [ ] Record demo video (optional)
- [ ] Prepare presentation slides

#### 7.5 Code Cleanup
- [ ] Remove debug print statements
- [ ] Add docstrings to all functions
- [ ] Format code consistently
- [ ] Remove unused imports

#### 7.6 Deployment Preparation
- [ ] Test on clean environment
- [ ] Verify all dependencies in requirements.txt
- [ ] Create deployment checklist
- [ ] Document Streamlit Cloud deployment

### Success Criteria
✅ All tests pass  
✅ Documentation complete  
✅ Demo ready  
✅ Code clean and documented  

### Deliverables
- Complete test suite
- Updated README.md
- Demo materials
- Deployment guide

---

## 🎯 Overall Progress Tracking

### Stage Completion Checklist
- [ ] Stage 1: Data & Parsers (Days 1-2)
- [ ] Stage 2: Feature Engineering (Days 3-4)
- [ ] Stage 3: ML Model (Days 4-6)
- [ ] Stage 4: Ranking & Explainability (Day 6)
- [ ] Stage 5: FastAPI Gateway (Day 7)
- [ ] Stage 6: Streamlit UI (Days 8-9)
- [ ] Stage 7: Testing & Documentation (Day 10)

### Current Status
**Stage:** Not Started  
**Next Action:** Begin Stage 1 - Data & Parsers  
**Blockers:** None  

---

**Ready to start Stage 1!** 🚀
