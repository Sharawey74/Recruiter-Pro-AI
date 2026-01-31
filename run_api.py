"""
Run the Recruiter Pro AI API Server
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run
from src.api import app
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Recruiter Pro AI API Server...")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
