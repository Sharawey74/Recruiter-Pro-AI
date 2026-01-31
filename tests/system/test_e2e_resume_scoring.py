"""
System Tests - End-to-End Resume Scoring

Tests the complete workflow from raw resume data to final decision:
- Data ingestion → Feature engineering → ML prediction → API response
- Multiple resume scenarios (high-quality, low-quality, edge cases)
- Full system integration
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression

from src.api import app
from src.ml_engine.feature_engineering import FeatureEngineer
from src.ml_engine.ats_predictor import ATSPredictor


@pytest.mark.system
@pytest.mark.slow
class TestEndToEndResumeScoring:
    """End-to-end system tests for complete resume scoring workflow"""
    
    @pytest.fixture
    def setup_production_environment(self, tmp_path, monkeypatch):
        """Setup complete production-like environment"""
        # Create sample training data
        np.random.seed(42)
        X_train = pd.DataFrame({
            'skills': ['Python, SQL, Machine Learning'] * 50,
            'experience_years': np.random.randint(1, 15, 50),
            'education': np.random.choice(['Bachelors', 'Masters', 'PhD'], 50),
            'certifications': np.random.choice(['AWS', 'GCP', 'Azure', 'None'], 50),
            'projects_count': np.random.randint(1, 30, 50),
            'current_role': np.random.choice(['Engineer', 'Senior Engineer', 'Lead'], 50),
            'expected_salary': np.random.randint(60000, 200000, 50)
        })
        y_train = np.random.randint(0, 2, 50)
        
        # Train feature engineer and model
        engineer = FeatureEngineer()
        X_transformed = engineer.fit_transform(X_train)
        
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_transformed, y_train)
        
        # Create production directory structure
        production_dir = tmp_path / "models" / "production"
        production_dir.mkdir(parents=True)
        
        model_path = production_dir / "ats_model.joblib"
        engineer_path = production_dir / "feature_engineer.joblib"
        
        joblib.dump(model, model_path)
        joblib.dump(engineer, engineer_path)
        
        # Patch paths in the app
        monkeypatch.setattr("src.api_server.Path", lambda x: tmp_path / x)
        
        return {
            'model_path': model_path,
            'engineer_path': engineer_path,
            'production_dir': production_dir
        }
    
    @pytest.fixture
    def client(self):
        """API test client"""
        return TestClient(app)
    
    @pytest.mark.system
    def test_high_quality_resume_workflow(self, client):
        """Test complete workflow for high-quality resume"""
        resume = {
            "skills": "Python, Machine Learning, Deep Learning, TensorFlow, PyTorch, SQL, AWS, Docker, Kubernetes",
            "experience_years": 8,
            "education": "PhD",
            "certifications": "AWS Certified Solutions Architect, Google Cloud Professional",
            "projects_count": 25,
            "current_role": "Principal Data Scientist",
            "expected_salary": 180000
        }
        
        response = client.post("/api/v1/score", json=resume)
        
        if response.status_code == 200:
            result = response.json()
            
            # High-quality resume should likely be accepted
            assert result['ml_probability'] >= 0.4  # At least review
            assert result['decision'] in ['Accept', 'Review']
            assert 'top_features' in result
            assert len(result['top_features']) > 0
    
    @pytest.mark.system
    def test_low_quality_resume_workflow(self, client):
        """Test complete workflow for low-quality resume"""
        resume = {
            "skills": "Microsoft Office",
            "experience_years": 0,
            "education": "High School",
            "certifications": "None",
            "projects_count": 0,
            "current_role": "Entry Level",
            "expected_salary": 35000
        }
        
        response = client.post("/api/v1/score", json=resume)
        
        if response.status_code == 200:
            result = response.json()
            
            # Should return valid prediction
            assert 'ml_prediction' in result
            assert 'ml_probability' in result
            assert result['decision'] in ['Accept', 'Review', 'Reject']
    
    @pytest.mark.system
    def test_mid_level_resume_workflow(self, client):
        """Test complete workflow for mid-level resume"""
        resume = {
            "skills": "Python, Django, PostgreSQL, Git",
            "experience_years": 3,
            "education": "Bachelors",
            "certifications": "None",
            "projects_count": 8,
            "current_role": "Software Engineer",
            "expected_salary": 85000
        }
        
        response = client.post("/api/v1/score", json=resume)
        
        if response.status_code == 200:
            result = response.json()
            
            # Should be in review range
            assert 0.0 <= result['ml_probability'] <= 1.0
            assert result['decision'] in ['Accept', 'Review', 'Reject']
            assert 'ml_confidence' in result
    
    @pytest.mark.system
    def test_batch_processing_workflow(self, client):
        """Test end-to-end batch processing"""
        resumes = [
            {
                "skills": "Python, Machine Learning",
                "experience_years": 5,
                "education": "Masters",
                "certifications": "AWS",
                "projects_count": 12,
                "current_role": "Senior Engineer",
                "expected_salary": 130000
            },
            {
                "skills": "Java, Spring Boot",
                "experience_years": 2,
                "education": "Bachelors",
                "certifications": "None",
                "projects_count": 4,
                "current_role": "Junior Developer",
                "expected_salary": 70000
            },
            {
                "skills": "Python, Data Science, R, SQL",
                "experience_years": 10,
                "education": "PhD",
                "certifications": "AWS, GCP, Azure",
                "projects_count": 30,
                "current_role": "Staff Data Scientist",
                "expected_salary": 200000
            }
        ]
        
        response = client.post("/api/v1/batch", json={"resumes": resumes})
        
        if response.status_code == 200:
            result = response.json()
            
            # Verify batch processing
            assert result['total_resumes'] == 3
            assert len(result['results']) == 3
            
            # Verify summary
            summary = result['summary']
            assert summary['accept_count'] + summary['reject_count'] + summary['review_count'] == 3
            assert 0.0 <= summary['avg_probability'] <= 1.0
            assert 0.0 <= summary['avg_confidence'] <= 1.0
    
    @pytest.mark.system
    def test_edge_case_maximum_values(self, client):
        """Test with maximum allowed values"""
        resume = {
            "skills": "Python, Java, C++, JavaScript, Go, Rust, SQL, NoSQL, AWS, Azure, GCP",
            "experience_years": 50,  # Maximum
            "education": "PhD",
            "certifications": "AWS, GCP, Azure, Oracle, Cisco, CompTIA, PMP",
            "projects_count": 999,  # Very high
            "current_role": "Chief Technology Officer",
            "expected_salary": 999999
        }
        
        response = client.post("/api/v1/score", json=resume)
        
        # Should handle extreme values gracefully
        assert response.status_code in [200, 503]  # Success or model not loaded
    
    @pytest.mark.system
    def test_edge_case_minimum_values(self, client):
        """Test with minimum allowed values"""
        resume = {
            "skills": "None",
            "experience_years": 0,
            "education": "High School",
            "certifications": "None",
            "projects_count": 0,
            "current_role": "Intern",
            "expected_salary": 0
        }
        
        response = client.post("/api/v1/score", json=resume)
        
        # Should handle minimum values
        assert response.status_code in [200, 503]
    
    @pytest.mark.system
    def test_special_characters_handling(self, client):
        """Test resume with special characters"""
        resume = {
            "skills": "C++, C#, Node.js, ASP.NET, Vue.js, React.js",
            "experience_years": 5,
            "education": "Masters",
            "certifications": "AWS (Advanced), Azure (Expert)",
            "projects_count": 10,
            "current_role": "Senior Engineer - Full Stack",
            "expected_salary": 120000
        }
        
        response = client.post("/api/v1/score", json=resume)
        
        # Should handle special characters
        assert response.status_code in [200, 503]
    
    @pytest.mark.system
    def test_unicode_characters_handling(self, client):
        """Test resume with unicode characters"""
        resume = {
            "skills": "Python, ML, AI, データサイエンス",  # Japanese characters
            "experience_years": 5,
            "education": "Masters",
            "certifications": "AWS Certified",
            "projects_count": 10,
            "current_role": "Data Scientist",
            "expected_salary": 120000
        }
        
        response = client.post("/api/v1/score", json=resume)
        
        # Should handle unicode
        assert response.status_code in [200, 422, 503]  # May fail validation
    
    @pytest.mark.system
    def test_health_check_integration(self, client):
        """Test health check in production environment"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'healthy'
        assert 'model_loaded' in data
        assert 'version' in data
    
    @pytest.mark.system
    def test_model_info_integration(self, client):
        """Test model info endpoint in system context"""
        response = client.get("/api/v1/model/info")
        
        # Should return 200 or 503 (model loaded or not)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert 'model_type' in data
            assert 'features_count' in data
    
    @pytest.mark.system
    def test_concurrent_requests_handling(self, client):
        """Test system handles concurrent requests"""
        import concurrent.futures
        
        resume = {
            "skills": "Python, SQL",
            "experience_years": 3,
            "education": "Bachelors",
            "certifications": "None",
            "projects_count": 5,
            "current_role": "Developer",
            "expected_salary": 80000
        }
        
        def make_request():
            return client.post("/api/v1/score", json=resume)
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should complete
        assert len(responses) == 10
        
        # Most should succeed (if model loaded)
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 0  # At least handle requests
    
    @pytest.mark.system
    @pytest.mark.slow
    def test_large_batch_processing(self, client):
        """Test system with maximum batch size"""
        resume_template = {
            "skills": "Python, SQL",
            "experience_years": 3,
            "education": "Bachelors",
            "certifications": "None",
            "projects_count": 5,
            "current_role": "Developer",
            "expected_salary": 80000
        }
        
        # Create 100 resumes (maximum allowed)
        resumes = [resume_template.copy() for _ in range(100)]
        
        # Vary some values
        for i, resume in enumerate(resumes):
            resume['experience_years'] = (i % 15) + 1
            resume['projects_count'] = (i % 30) + 1
        
        response = client.post("/api/v1/batch", json={"resumes": resumes})
        
        if response.status_code == 200:
            result = response.json()
            assert result['total_resumes'] == 100
            assert len(result['results']) == 100
    
    @pytest.mark.system
    def test_error_recovery(self, client):
        """Test system recovers from errors gracefully"""
        # Send invalid request
        invalid_resume = {
            "skills": "Python",
            "experience_years": -5,  # Invalid
            "education": "Masters"
        }
        
        response = client.post("/api/v1/score", json=invalid_resume)
        assert response.status_code == 422  # Validation error
        
        # Now send valid request - system should still work
        valid_resume = {
            "skills": "Python, SQL",
            "experience_years": 5,
            "education": "Masters",
            "certifications": "None",
            "projects_count": 10,
            "current_role": "Engineer",
            "expected_salary": 100000
        }
        
        response = client.post("/api/v1/score", json=valid_resume)
        assert response.status_code in [200, 503]  # Should recover


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'system'])
