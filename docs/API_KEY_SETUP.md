# 🔑 Quick Setup - Your API Keys

## ✅ Your Configuration

You have **two separate API keys** for different models:

### Agent 3 (Scorer) - GPT-OSS-20B
- **API Key**: `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`
- **Model**: `openai/gpt-oss-20b`
- **Purpose**: Fast scoring for batch processing

### Agent 4 (Decision Engine) - GPT-OSS-120B
- **API Key**: `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`
- **Model**: `openai/gpt-oss-120b`
- **Purpose**: Detailed explanations

---

## 📝 Update Your .env File

Open `c:\Users\DELL\Desktop\HR-Project\.env` and add these lines:

```bash
# ============================================
# LLM API Configuration
# ============================================

# OpenRouter Base URL
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Agent 3 (Scorer) - GPT-OSS-20B
AGENT3_API_KEY=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
AGENT3_MODEL=openai/gpt-oss-20b

# Agent 4 (Decision Engine) - GPT-OSS-120B
AGENT4_API_KEY=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
AGENT4_MODEL=openai/gpt-oss-120b

# Ollama Configuration (for Agent 5)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Model Thresholds
MODEL_CONFIDENCE_THRESHOLD=0.60
HIGH_MATCH_THRESHOLD=0.75
MEDIUM_MATCH_THRESHOLD=0.50

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DOCS_ENABLED=true
CORS_ORIGINS=http://localhost:8501,http://localhost:3000

# Streamlit Configuration
STREAMLIT_PORT=8501
MAX_UPLOAD_SIZE_MB=10

# Data Paths
JOBS_DATA_PATH=data/json/jobs.json
PARSED_PROFILES_DIR=data/json/parsed_profiles
RESULTS_DIR=data/json/results
REPORTS_DIR=data/reports

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
REQUEST_TIMEOUT=30

# Feature Flags
ENABLE_LLM_SCORING=true
ENABLE_LLM_EXPLANATIONS=true
ENABLE_ANALYTICS_LLM=true
FALLBACK_TO_RULES=true
```

---

## ✅ What Changed

### Before (Single Key):
```bash
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
```

### After (Separate Keys):
```bash
AGENT3_API_KEY=sk-or-v1-8356... (GPT-20B)
AGENT3_MODEL=openai/gpt-oss-20b

AGENT4_API_KEY=sk-or-v1-45fb... (GPT-120B)
AGENT4_MODEL=openai/gpt-oss-120b
```

---

## 🔄 Fallback Support

The agents now support **fallback** to a shared key:

```python
# Agent 3 tries in order:
1. AGENT3_API_KEY (if set)
2. OPENROUTER_API_KEY (fallback)

# Agent 4 tries in order:
1. AGENT4_API_KEY (if set)
2. OPENROUTER_API_KEY (fallback)
```

This means you can:
- Use separate keys (recommended)
- Use one shared key for both
- Mix and match

---

## 🚀 Ready to Run!

After updating your `.env` file:

```bash
# Start FastAPI
python src\api.py

# Start Streamlit
streamlit run streamlit_app\app.py
```

---

## 🎯 Model Comparison

| Feature | GPT-OSS-20B (Agent 3) | GPT-OSS-120B (Agent 4) |
|---------|----------------------|------------------------|
| **Parameters** | 20 Billion | 120 Billion |
| **Speed** | Fast | Moderate |
| **Quality** | Good | Excellent |
| **Use Case** | Scoring 500+ jobs | Detailed explanations |
| **Cost** | Lower | Higher |

**Why separate models?**
- Agent 3 processes **many jobs** → needs speed
- Agent 4 generates **detailed text** → needs quality

---

**Status**: ✅ Configuration Updated  
**Next**: Update your `.env` file and start the servers!
