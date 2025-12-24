# 📋 STAGE 5: Agent 5 (Analytics & Optimization Engine)

## Goal
Implement an analytics engine that aggregates results, generates insights, and provides optimization suggestions using local LLM (LLaMA3.1:8B) with LangChain/CrewAI for structured reasoning.

## Architecture
- **Core Type**: Analytics + Local LLM + LangChain/CrewAI
- **LLM Use**: YES - Generate optimization insights and improvement suggestions
- **LangChain / CrewAI**: ✅ USE for structured reasoning pipelines (metrics → insights → report)
- **API vs Local**: Local LLM (cheaper, faster, offline)
- **Recommended Model**: LLaMA3.1:8B via Ollama
  - **Pros**: Larger model, higher reasoning capacity, better context understanding
  - **Cons**: Bigger memory footprint (4.9 GB), slightly slower
  - **Why**: ✅ Best for generating high-quality insights from complex analytics data

## Tasks
- [ ] **Setup Local LLM Environment**
    - [ ] Install `ollama` and download `llama3.1:8b` model.
    - [ ] Install `langchain` and `langchain-community`.
    - [ ] Install `crewai` (optional - for multi-agent reasoning).
- [ ] **Implement Metrics Aggregation**
    - [ ] Create `src/agents/agent5_analytics.py`.
    - [ ] Load all decisions from `data/processed/final_decisions/`.
    - [ ] Compute key metrics:
        - Total candidates processed
        - SHORTLIST / REVIEW / REJECT counts and percentages
        - Average confidence scores per decision category
        - Top missing skills across all candidates
        - Most common rejection reasons
        - Experience gap analysis
- [ ] **Implement Visualization**
    - [ ] Generate pipeline funnel chart (Plotly).
    - [ ] Generate score distribution histogram.
    - [ ] Generate skills gap heatmap.
    - [ ] Save as PNG/HTML in `data/reports/`.
- [ ] **LLM Insight Generation with LangChain**
    - [ ] Create LangChain pipeline: Metrics → Analysis → Insights.
    - [ ] Prompt LLaMA3.1: "Analyze these hiring metrics and suggest improvements..."
    - [ ] Generate structured insights:
        - Job description optimization recommendations
        - Skill requirement adjustments
        - Experience range calibration
        - Process efficiency suggestions
- [ ] **CrewAI Multi-Agent Reasoning (Optional)**
    - [ ] Create specialized agents:
        - **Data Analyst Agent**: Interprets metrics
        - **HR Advisor Agent**: Suggests hiring process improvements
        - **Report Writer Agent**: Generates final report
    - [ ] Orchestrate agents to produce comprehensive analytics report.
- [ ] **Report Generation**
    - [ ] Generate HTML analytics dashboard.
    - [ ] Save JSON summary: `data/reports/analytics_summary.json`.
    - [ ] Include actionable recommendations.

## Implementation Notes
- **Tech Stack**: Python, Pandas, Plotly, Ollama, LangChain, CrewAI (optional).
- **Type**: Analytics + Local LLM reasoning.
- **Integration**: Consumes Agent 4 Results, produces final reports.
- **Offline capability**: Works without internet (local LLM).

## LangChain Pipeline Structure
```python
# Metrics Collection → LLM Analysis → Insights Generation
chain = (
    MetricsPromptTemplate 
    | OllamaLLM(model="llama3.1:8b")
    | InsightParser
    | RecommendationGenerator
)
```

## Unit & Integration Testing
- [ ] **Unit Test 1**: Test metric calculation on dummy batch results.
- [ ] **Unit Test 2**: Test visualization generation.
- [ ] **Unit Test 3**: Test LLM insight generation (mock Ollama).
- [ ] **Integration Test**: Full pipeline → Agent 5 → Analytics Report with LLM insights.

## Deliverables
- `src/agents/agent5_analytics.py`
- `data/reports/analytics_dashboard.html`
- `data/reports/analytics_summary.json`
- `data/reports/visualizations/*.png`
- `tests/test_agent5_analytics.py`

## Success Criteria
✅ Correctly aggregates all metrics from Agent 4 results.
✅ Generates clear visualizations (funnel, distributions, heatmaps).
✅ LLM produces actionable insights (at least 3 specific recommendations).
✅ Identifies patterns (e.g., "High rejection rate due to Python skill gaps").
✅ Works offline with local LLaMA model.
✅ HTML report is readable and professional.

