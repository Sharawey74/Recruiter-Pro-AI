# 📋 STAGE 2: Agent 2 (NLP Extraction)

## Goal
Implement an NLP-based agent to transform raw text blocks (from Agent 1) into structured, normalized data extraction (Skills, Experience, Education).

## Tasks
- [ ] **Setup NLP Environment**
    - [ ] Install `spacy` and download `en_core_web_sm`.
    - [ ] Install `nltk`.
- [ ] **Implement Extraction Logic**
    - [ ] Create `src/agents/agent2_extractor.py`.
    - [ ] Implement `extract_skills(text)` using SpaCy NER and pattern matching.
    - [ ] Implement `extract_experience_years(text)` using regex and date parsing.
    - [ ] Implement `extract_education_level(text)` (Bachelor, Master, PhD).
- [ ] **Implement Normalization**
    - [ ] Map synonyms to canonical forms (e.g., "React.js" -> "React", "AWS EC2" -> "AWS").
    - [ ] Deduplicate skills.
- [ ] **Output Generation**
    - [ ] Input: `data/processed/raw_profiles/{id}.json`.
    - [ ] Output: `data/processed/structured_profiles/{id}.json`.
    - [ ] Schema: `{"skills": [...], "experience_years": 5, "education": "Master", ...}`.

## Implementation Notes
- **Tech Stack**: Python, SpaCy, NLTK.
- **Type**: NLP Extraction.
- **Integration**: Consumes Agent 1 Output, feeds Agent 3.

## Unit & Integration Testing
- [ ] **Unit Test 1**: Test skill extraction on a text block with known skills.
- [ ] **Unit Test 2**: Test experience calculation (dates provided in text).
- [ ] **Unit Test 3**: Test normalization (input "React.js", expect "React").
- [ ] **Integration Test**: Agent 1 Output JSON -> Agent 2 -> Structured JSON.

## Deliverables
- `src/agents/agent2_extractor.py`
- `data/dictionaries/skills_canonical.json` (mapping file)
- `tests/test_agent2_extraction.py`

## Success Criteria
✅ Extracts >80% of skills correctly compared to ground truth.
✅ Correctly identifies years of experience within +/- 1 year.
✅ Normalized output contains no duplicates.
