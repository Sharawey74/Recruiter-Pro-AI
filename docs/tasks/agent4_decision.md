# 📋 STAGE 4: Agent 4 (Decision & Explanation Engine)

## Goal
Implement a hybrid decision engine (Rules + LLM) that takes Agent 3 LLM scores and applies business rules to produce final hiring decisions (SHORTLIST / REVIEW / REJECT) with human-readable explanations.

## Architecture
- **Core Type**: Rules + LLM (API-based)
- **LLM Use**: YES - For explanation generation and final scoring alignment
- **LangChain / CrewAI**: ❌ NOT NEEDED for Agent 4
- **API vs Local**: API-based (OpenRouter/GPT)
- **Recommended Model**: GPT-OSS-20B (high-quality reasoning, semantic explanations)

## Tasks
- [ ] **Setup Configuration**
    - [ ] Create `config/decision_rules.yaml` (Thresholds, business rules).
    - [ ] Define decision thresholds (e.g., High > 0.75 = SHORTLIST).
- [ ] **Implement Decision Logic**
    - [ ] Create `src/agents/agent4_decision.py`.
    - [ ] **Rule 1**: SHORTLIST if Agent 3 score ≥ 0.75 (High match).
    - [ ] **Rule 2**: REVIEW if Agent 3 score 0.50-0.74 (Medium match).
    - [ ] **Rule 3**: REJECT if Agent 3 score < 0.50 (Low match).
    - [ ] **Rule 4**: Flag overqualification warnings.
    - [ ] **Rule 5**: Check for critical skill gaps.
- [ ] **LLM Explanation Generation**
    - [ ] Use GPT-OSS-20B to generate human-readable explanations.
    - [ ] Prompt: "Explain why this candidate is [decision] for this role..."
    - [ ] Include strengths, weaknesses, and specific recommendations.
- [ ] **Ranking & Prioritization**
    - [ ] Rank candidates by: (1) Decision Category, (2) Confidence Score.
    - [ ] Within SHORTLIST, rank by Agent 3 confidence.
- [ ] **Output Generation**
    - [ ] Output: `data/processed/final_decisions/{batch_id}_decisions.json`.
    - [ ] Schema: `{"decision": "SHORTLIST", "confidence": 0.85, "explanation": "...", "ranking": 1}`.

## Implementation Notes
- **Tech Stack**: Python, `openai` SDK, YAML config.
- **Type**: Hybrid (Rule-based + LLM explanations).
- **Integration**: Consumes Agent 3 Output, feeds Agent 5.
- **No frameworks**: Pure Python + OpenAI SDK (no LangChain/CrewAI).

## Unit & Integration Testing
- [ ] **Unit Test 1**: Test decision rules with various score ranges.
- [ ] **Unit Test 2**: Test LLM explanation generation (mock API).
- [ ] **Unit Test 3**: Test ranking algorithm.
- [ ] **Integration Test**: Agent 3 Output → Agent 4 → Final Decisions with explanations.

## Deliverables
- `src/agents/agent4_decision.py`
- `config/decision_rules.yaml`
- `tests/test_agent4_decision.py`

## Success Criteria
✅ Correctly categorizes candidates (SHORTLIST/REVIEW/REJECT).
✅ Generates clear, actionable explanations for each decision.
✅ Ranks candidates properly within categories.
✅ Handles API failures gracefully.
✅ Explanations are context-aware and helpful for recruiters.

