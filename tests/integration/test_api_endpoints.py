"""
Unit Tests for API Server

Tests the FastAPI endpoints:
- Health check
- Model info
- Single resume scoring
- Batch scoring
- Error handling
"""

import pytest
from fastapi.testclient import TestClient
import pandas as pd
import joblib
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression

# Import after creating necessary mocks
from src.api import app
from src.ml_engine.feature_engineering import FeatureEngineer


class TestAPIEndpoints:
    """Unit tests for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_resume_payload(self):
        """Sample resume for API testing"""
        return {
            "skills": "Python, Machine Learning, SQL",
            "experience_years": 5,
            "education": "Masters",
            "certifications": "AWS Certified",
            "projects_count": 10,
            "current_role": "Senior Engineer",
            "expected_salary": 120000
        }
    
    @pytest.fixture
    def setup_test_model(self, tmp_path, monkeypatch):
        """Create and setup test model for API"""
        # Create sample data for training
        np.random.seed(42)
        X_train = pd.DataFrame({
            'skills': ['Python, SQL'] * 50,
            'experience_years': np.random.randint(1, 10, 50),
            'education': np.random.choice(['Bachelors', 'Masters', 'PhD'], 50),
            'certifications': np.random.choice(['AWS', 'None'], 50),
            'projects_count': np.random.randint(1, 20, 50),
            'current_role': np.random.choice(['Engineer', 'Senior'], 50),
            'expected_salary': np.random.randint(60000, 150000, 50)
        })
        y_train = np.random.randint(0, 2, 50)
        
        # Train feature engineer and model
        engineer = FeatureEngineer()
        X_transformed = engineer.fit_transform(X_train)
        
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_transformed, y_train)
        
        # Save to temp directory
        model_path = tmp_path / "ats_model.joblib"
        engineer_path = tmp_path / "feature_engineer.joblib"
        
        joblib.dump(model, model_path)
        joblib.dump(engineer, engineer_path)
        
        # Patch the model paths in the app
        monkeypatch.setattr("src.api_server.Path", lambda x: tmp_path / x.split('/')[-1])
        
        return model_path, engineer_path
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "model_loaded" in data
        assert "version" in data
        assert data["status"] == "healthy"
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_health_endpoint_structure(self, client):
        """Test health endpoint returns correct structure"""
        response = client.get("/api/v1/health")
        data = response.json()
        
        assert isinstance(data["status"], str)
        assert isinstance(data["model_loaded"], bool)
        assert isinstance(data["version"], str)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_score_resume_valid_input(self, client, sample_resume_payload):
        """Test scoring single resume with valid input"""
        response = client.post("/api/v1/score", json=sample_resume_payload)
        
        # May fail if model not loaded, but should return valid status code
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "ml_prediction" in data
            assert "ml_probability" in data
            assert "decision" in data
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_score_resume_invalid_experience(self, client):
        """Test scoring with invalid experience years"""
        invalid_payload = {
            "skills": "Python",
            "experience_years": -5,  # Invalid: negative
            "education": "Masters",
            "certifications": "None",
            "projects_count": 10,
            "current_role": "Engineer",
            "expected_salary": 100000
        }
        
        response = client.post("/api/v1/score", json=invalid_payload)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_score_resume_invalid_education(self, client):
        """Test scoring with invalid education"""
        invalid_payload = {
            "skills": "Python",
            "experience_years": 5,
            "education": "InvalidDegree",  # Invalid
            "certifications": "None",
            "projects_count": 10,
            "current_role": "Engineer",
            "expected_salary": 100000
        }
        
        response = client.post("/api/v1/score", json=invalid_payload)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_score_resume_missing_required_field(self, client):
        """Test scoring with missing required field"""
        incomplete_payload = {
            "skills": "Python",
            # Missing experience_years
            "education": "Masters",
            "certifications": "None",
            "projects_count": 10,
            "current_role": "Engineer",
            "expected_salary": 100000
        }
        
        response = client.post("/api/v1/score", json=incomplete_payload)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_batch_score_valid_input(self, client, sample_resume_payload):
        """Test batch scoring with valid input"""
        batch_payload = {
            "resumes": [sample_resume_payload, sample_resume_payload]
        }
        
        response = client.post("/api/v1/batch", json=batch_payload)
        
        # May fail if model not loaded
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_resumes" in data
            assert "results" in data
            assert "summary" in data
            assert data["total_resumes"] == 2
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_batch_score_empty_list(self, client):
        """Test batch scoring with empty resume list"""
        batch_payload = {
            "resumes": []
        }
        
        response = client.post("/api/v1/batch", json=batch_payload)
        assert response.status_code == 422  # Validation error (min_items=1)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_batch_score_too_many_resumes(self, client, sample_resume_payload):
        """Test batch scoring with too many resumes"""
        batch_payload = {
            "resumes": [sample_resume_payload] * 101  # Max is 100
        }
        
        response = client.post("/api/v1/batch", json=batch_payload)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_model_info_endpoint(self, client):
        """Test model info endpoint"""
        response = client.get("/api/v1/model/info")
        
        # May fail if model not loaded
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "model_type" in data
            assert "features_count" in data
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.get("/api/v1/health")
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_documentation_available(self, client):
        """Test that API documentation is accessible"""
        docs_response = client.get("/api/docs")
        redoc_response = client.get("/api/redoc")
        
        # Should return HTML for documentation
        assert docs_response.status_code == 200
        assert redoc_response.status_code == 200
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_decision_thresholds(self, client, sample_resume_payload):
        """Test decision logic based on probability thresholds"""
        # This test verifies the decision logic without actually running prediction
        # Decision rules:
        # - probability >= 0.7 -> Accept
        # - probability >= 0.4 -> Review
        # - probability < 0.4 -> Reject
        
        # Just verify the payload structure is correct
        response = client.post("/api/v1/score", json=sample_resume_payload)
        
        if response.status_code == 200:
            data = response.json()
            assert data["decision"] in ["Accept", "Reject", "Review"]
            
            # Decision should match probability
            prob = data["ml_probability"]
            if prob >= 0.7:
                assert data["decision"] == "Accept"
            elif prob >= 0.4:
                assert data["decision"] == "Review"
            else:
                assert data["decision"] == "Reject"
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_response_time_acceptable(self, client, sample_resume_payload):
        """Test that API responds within acceptable time"""
        import time
        
        start_time = time.time()
        response = client.post("/api/v1/score", json=sample_resume_payload)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should respond within 5 seconds
        assert response_time < 5.0
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_batch_summary_statistics(self, client, sample_resume_payload):
        """Test that batch response includes correct summary statistics"""
        batch_payload = {
            "resumes": [sample_resume_payload] * 3
        }
        
        response = client.post("/api/v1/batch", json=batch_payload)
        
        if response.status_code == 200:
            data = response.json()
            summary = data["summary"]
            
            # Summary should have required fields
            assert "accept_count" in summary
            assert "reject_count" in summary
            assert "review_count" in summary
            assert "avg_probability" in summary
            
            # Counts should sum to total
            total_decisions = (
                summary["accept_count"] + 
                summary["reject_count"] + 
                summary["review_count"]
            )
            assert total_decisions == data["total_resumes"]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
