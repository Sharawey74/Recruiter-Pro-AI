import pandas as pd
import numpy as np
import joblib
import re
import os
import sys
from pathlib import Path

class ATSEngine:
    def __init__(self):
        self.model = None
        self.model_path = Path("ML/ML2/models/opt_rf_model.joblib")
        # Default placeholder model if file missing (for robust startup)
        self.use_mock = False 
        
    def initialize(self):
        """Load the ML2 model"""
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                print(f"✅ ML2 Model loaded from {self.model_path}")
            except Exception as e:
                print(f"❌ Failed to load ML2 model: {e}")
                self.use_mock = True
        else:
            print(f"⚠️ ML2 Model not found at {self.model_path}. Using mock mode.")
            self.use_mock = True

    def predict(self, cv_text: str, metadata: dict = None) -> dict:
        """
        Predict ATS Score for a CV
        
        Args:
            cv_text: Extracted text from CV
            metadata: Dict with parsed fields e.g., {'Experience (Years)': 5, 'Skills': '...'}
            
        Returns:
            dict: {
                'ats_score': float (0-100),
                'risk_level': str ('LOW', 'MEDIUM', 'HIGH'),
                'assessment': str
            }
        """
        if not metadata:
            metadata = {}
            
        # 1. Prepare raw dataframe (1 row)
        # We need to map extracted metadata to the columns expected by FeatureEngineer
        # Expected raw columns: 'Skills', 'Certifications', 'Job Role', 'Experience (Years)', 'Projects Count', 'Salary Expectation ($)'
        
        # Defaults if parsing failed
        raw_data = {
            'Skills': metadata.get('skills', '') or cv_text, # Fallback to text if skills not parsed
            'Certifications': metadata.get('certifications', 'None'),
            'Job Role': metadata.get('role', 'Software Engineer'), # Default role
            'Experience (Years)': self._parse_experience(metadata.get('experience', 0)),
            'Projects Count': metadata.get('projects_count', 2), # Default assumption
            'Salary Expectation ($)': 0, # Neutral default
            'Education': metadata.get('education', 'Bachelor degree') # Fix: Added missing column
        }
        
        df = pd.DataFrame([raw_data])
        
        # 2. Feature Engineering (Replicated from ML2/src/features.py)
        df_enhanced = self._feature_engineering(df)
        
        # 3. Prediction
        if self.use_mock:
            # Mock logic based on keywords
            score = 65.0
            if 'python' in cv_text.lower(): score += 10
            if 'experience' in cv_text.lower(): score += 5
            score = min(95, score)
        else:
            try:
                # Predict Probability of Class 1 (Hire)
                # Ensure input columns match pipeline expectation
                # The pipeline handles scaling/encoding, so we just pass df_enhanced
                probs = self.model.predict_proba(df_enhanced)
                score = probs[0][1] * 100  # Scale 0-1
            except Exception as e:
                print(f"Prediction Error: {e}")
                score = 50.0 # Fallback

        # 4. Result Formatting
        risk_level = "HIGH"
        if score >= 75:
            risk_level = "LOW"
        elif score >= 50:
            risk_level = "MEDIUM"
            
        return {
            "ats_score": round(score, 1),
            "risk_level": risk_level,
            "assessment": self._get_assessment(score)
        }

    def _parse_experience(self, exp):
        """Parse experience to float"""
        if isinstance(exp, (int, float)):
            return float(exp)
        if isinstance(exp, str):
            # Extract first number
            match = re.search(r'\d+', exp)
            if match:
                return float(match.group())
        return 2.0 # Default to junior

    def _feature_engineering(self, df):
        """Replicate ML2 feature engineering"""
        df = df.copy()
        
        # 2.1 Skills Semantics
        df['Skills_Clean'] = df['Skills'].astype(str).apply(self._clean_skills)
        df['Skill_Count'] = df['Skills'].astype(str).apply(lambda x: len(x.split(',')) if x != 'nan' else 0)
        
        # 2.2 Structured Feature Enhancement
        df['Cert_Count'] = df['Certifications'].astype(str).apply(lambda x: 0 if x in ['None', 'nan'] else 1)
        df['Cert_Impact'] = df['Certifications'].astype(str).apply(self._calc_cert_score)
        
        # Role Level
        role_map = {
            'Software Engineer': 1,
            'Cybersecurity Analyst': 1.2,
            'Data Scientist': 1.5,
            'AI Researcher': 1.8
        }
        # Fuzzy map or default
        df['Role_Level'] = df['Job Role'].map(role_map).fillna(1.0)
        
        df['Seniority_Index'] = df['Experience (Years)'] * df['Role_Level']
        df['Exp_Weighted_Skills'] = df['Skill_Count'] * (np.log1p(df['Experience (Years)']))
        df['Project_Intensity'] = df['Projects Count'] / (df['Experience (Years)'] + 1)
        df['Value_Density'] = df['Salary Expectation ($)'] / (df['Experience (Years)'] + 1)
        
        return df

    def _clean_skills(self, text):
        if pd.isnull(text): return ""
        text = text.lower()
        text = re.sub(r'[^\w\s,]', '', text)
        return text

    def _calc_cert_score(self, text):
        if text in ['None', 'nan', '']:
            return 0
        score = 1
        text = text.lower()
        if 'certified' in text or 'specialization' in text:
            score += 1
        if 'google' in text or 'aws' in text: 
            score += 1
        return score

    def _get_assessment(self, score):
        if score >= 85: return "Excellent profile! High probability of being shortlisted."
        if score >= 70: return "Strong profile. Good match for most roles."
        if score >= 50: return "Average capability. May need more specific skills."
        return "Needs improvement. Consider adding more keywords or experience."
