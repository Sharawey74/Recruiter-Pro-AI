# 📋 STAGE 3: Agent 3 (LLM API Scorer)

## Goal
Implement an LLM-based agent to semantically score the match between a candidate's structured profile (Agent 2) and a job description, providing high-accuracy reasoning.

## Tasks
- [ ] **Setup LLM Client**
    - [ ] Configure `openai` client for OpenRouter (GPT-OSS-20B or equivalent).
    - [ ] Create `src/agents/agent3_scorer.py`.
- [ ] **Prompt Engineering**
    - [ ] Design system prompt: "You are an expert HR recruiter...".
    - [ ] Design user prompt: Pass JSON profile + Job Description.
    - [ ] Output constraint: Enforce strict JSON output (Score, Confidence, Reasoning).
- [ ] **Implement Scoring Logic**
    - [ ] Function `score_candidate(profile_json, job_json)`.
    - [ ] Handle API errors/rate limits (Exponential backoff).
    - [ ] Fallback mechanism: If API fails, return error or basic keyword overlap score.
- [ ] **Output Generation**
    - [ ] Output: `data/processed/scored_matches/{profile_id}_{job_id}.json`.
    - [ ] Schema: `{"match_score": 0.85, "confidence": 0.9, "reasoning": "..."}`.

## Implementation Notes
- **Tech Stack**: Python, `openai` (SDK), OpenRouter API.
- **Type**: LLM Semantic Scorer.
- **Integration**: Consumes Agent 2 Output, feeds Agent 4.
- **Cost Management**: Monitor token usage per call.

## Unit & Integration Testing
- [ ] **Unit Test 1**: Mock API response and test JSON parsing.
- [ ] **Unit Test 2**: Test prompt construction with various profile/job inputs.
- [ ] **Integration Test**: Agent 2 Output -> Agent 3 -> Scored JSON.

## Deliverables
- `src/agents/agent3_scorer.py`
- `tests/test_agent3_scoring.py`

## Success Criteria
✅ Successfully receives valid JSON from LLM API.
✅ Handles API failures gracefully (no crashes).
✅ JSON parsing is robust (handling potential markdown wrapping).
