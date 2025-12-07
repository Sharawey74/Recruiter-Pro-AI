# 🎯 Resume-Job Matching Multi-Agent System

A college project implementing an intelligent resume-job matching system using multi-agent architecture with ML classification and rule-based reasoning.

## 📊 Project Overview

- **Training Data:** 35,730 labeled resume-job pairs
- **Model:** Random Forest Classifier with probability-based scoring
- **Agents:** 4 specialized agents (Parser, Features, Scorer, Analytics)
- **Deployment:** Streamlit Cloud
- **Tech Stack:** Python, FastAPI, Streamlit, scikit-learn, spaCy

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download spaCy language model
python -m spacy download en_core_web_sm

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your API keys (optional for LLM features)

# 4. Prepare data
python scripts/prepare_jobs_json.py

# 5. Train the model
python scripts/train_models.py
```

### Running the Application

```bash
# Start FastAPI backend (Terminal 1)
uvicorn src.api:app --reload --port 8000

# Start Streamlit UI (Terminal 2)
streamlit run streamlit_app/app.py
```

Then open your browser to:
- **Streamlit UI:** http://localhost:8501
- **FastAPI Docs:** http://localhost:8000/docs

## 📁 Project Structure

```
resume-job-matching/
├── data/                      # Data files
│   ├── raw/                   # Original dataset
│   └── json/                  # JSON data files
├── models/                    # Trained ML models
├── src/                       # Source code
│   ├── agents/                # Agent implementations
│   ├── utils/                 # Utility functions
│   └── api.py                 # FastAPI application
├── streamlit_app/             # Streamlit UI
├── tests/                     # Unit tests
├── scripts/                   # Utility scripts
└── config/                    # Configuration files
```

## 🤖 Agent Architecture

### Agent 1: Profile & Job Parser
- **Tech:** spaCy + NLTK fallback
- **Input:** Raw CV text or job description
- **Output:** Structured JSON with skills, experience, education

### Agent 2: Feature Generator
- **Tech:** Pandas, NumPy, scikit-learn
- **Input:** Parsed profile + job
- **Output:** Feature vectors (skill overlap, experience match, etc.)

### Agent 2.5: ML Scorer
- **Tech:** Random Forest Classifier + Rule Engine
- **Input:** Feature vectors
- **Output:** Match label (High/Medium/Low) with probabilities

### Agent 3: Decision & Ranking Engine
- **Tech:** Business rules + optional LLM explanations
- **Input:** ML predictions
- **Output:** Final decisions with explanations

### Agent 4: Analytics & Logging
- **Tech:** Streamlit dashboards, Pandas
- **Input:** System logs
- **Output:** Performance metrics and insights

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src

# Run specific test file
pytest tests/test_agent1_parser.py -v
```

## 📊 Model Performance

- **Accuracy:** ~79% on validation set
- **Classes:** High, Medium, Low (balanced)
- **Features:** TF-IDF (1000 features) + engineered features
- **Training Data:** 25,011 samples
- **Validation:** 5,359 samples
- **Test:** 5,360 samples

## 🔧 Configuration

### Environment Variables (.env)

```bash
# LLM API (optional - for Agent 3 explanations)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4

# Model thresholds
MODEL_CONFIDENCE_THRESHOLD=0.60
HIGH_MATCH_THRESHOLD=0.85
MEDIUM_MATCH_THRESHOLD=0.60
```

### Business Rules (config/rules.yaml)

```yaml
decision_rules:
  high_confidence_threshold: 0.85
  medium_confidence_threshold: 0.60
  low_confidence_floor: 0.35
```

## 📖 API Endpoints

### POST /match
Match a profile against jobs

```bash
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{"profile_text": "5 years Python developer..."}'
```

### GET /jobs
Get all available job templates

```bash
curl http://localhost:8000/jobs
```

## 🎓 Usage Examples

### 1. Upload CV via Streamlit
1. Navigate to http://localhost:8501
2. Upload or paste CV text
3. System auto-detects role
4. View top job matches with explanations

### 2. API Integration
```python
import requests

response = requests.post(
    "http://localhost:8000/match",
    json={"profile_text": "Senior Python Developer with 5 years..."}
)

matches = response.json()
print(f"Top match: {matches['top_matches'][0]}")
```

## 🚀 Deployment (Streamlit Cloud)

1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Set environment variables in Streamlit dashboard
4. Deploy from `streamlit_app/app.py`

## 📝 Development Workflow

### Adding a New Feature

1. Update relevant agent in `src/agents/`
2. Add unit tests in `tests/`
3. Update API endpoint if needed
4. Update Streamlit UI if needed
5. Run tests: `pytest tests/ -v`

### Retraining the Model

```bash
# After updating training data
python scripts/train_models.py

# Test new model
python src/agents/agent2_5_scorer.py
```

## 🐛 Troubleshooting

### spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

### Models not found
```bash
python scripts/train_models.py
```

### Port already in use
```bash
# Change port in command
uvicorn src.api:app --reload --port 8001
streamlit run streamlit_app/app.py --server.port 8502
```

## 📚 Documentation

- **Dataset Documentation:** See `DATASET_DOCUMENTATION.md`
- **Project Summary:** See `PROJECT_SUMMARY.md`
- **API Documentation:** http://localhost:8000/docs (when running)

## 👥 Contributors

College Project - HR Resume-Job Matching System

## 📄 License

Educational/Academic Use

## 🙏 Acknowledgments

- Training dataset: `final_training_dataset_v2.csv` (35,730 records)
- spaCy for NLP processing
- scikit-learn for ML models
- FastAPI for API framework
- Streamlit for UI

---

**Status:** ✅ Ready for Development  
**Last Updated:** December 7, 2025
