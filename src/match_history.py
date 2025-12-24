"""
Match History Manager
Handles saving and loading match results for analytics
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import uuid


class MatchHistoryManager:
    """Manages match history storage and retrieval"""
    
    def __init__(self, history_file: str = "data/match_history.json"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize file if it doesn't exist
        if not self.history_file.exists():
            self._save_to_file([])
    
    def _load_from_file(self) -> List[Dict]:
        """Load match history from JSON file"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_to_file(self, data: List[Dict]):
        """Save match history to JSON file"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _generate_id(self) -> str:
        """Generate a unique ID for a match."""
        return str(uuid.uuid4())

    def save_match(self, match_data: Dict) -> str:
        """
        Save a single match to history
        
        Args:
            match_data: Dictionary containing match information
            
        Returns:
            match_id: Unique identifier for this match
        """
        match_id = self._generate_id()
        
        # Add metadata
        match_record = {
            "match_id": match_id,
            "timestamp": datetime.now().isoformat(),
            "candidate_name": match_data.get('candidate_name', 'Unknown'),
            "job_title": match_data.get('job_title', 'Unknown'),
            "job_id": match_data.get('job_id', 'N/A'),
            "decision": match_data.get('decision', 'REVIEW'),
            "confidence": match_data.get('confidence', 0.0),
            "match_label": match_data.get('match_label', 'Medium'),
            "matched_skills": match_data.get('matched_skills', []),
            "missing_skills": match_data.get('missing_skills', []),
            "experience_match_score": match_data.get('experience_match_score', 0.0),
            "skill_match_score": match_data.get('skill_match_score', 0.0),
            "ats_score": match_data.get('ats_score', 0.0),
            "explanation": match_data.get('explanation', ''),
            "ai_explanation": match_data.get('ai_explanation')  # NEW: Agent 4 output
        }
        
        # Load existing history
        history = self._load_from_file()
        
        # Add new match
        history.append(match_record)
        
        # Save updated history
        self._save_to_file(history)
        
        return match_id
    
    
    def save_batch_matches(self, candidate_name: str, matches: List[Dict]) -> List[str]:
        """
        Save multiple matches from a single candidate
        
        Args:
            candidate_name: Name of the candidate
            matches: List of match dictionaries
            
        Returns:
            List of match IDs
        """
        match_ids = []
        
        for match in matches:
            # Create a flat copy to avoid modifying original
            flat_match = match.copy()
            flat_match['candidate_name'] = candidate_name
            
            # Flatten nested skill_match if present (Fix for Data Loss)
            if 'skill_match' in match and isinstance(match['skill_match'], dict):
                skill_data = match['skill_match']
                flat_match['matched_skills'] = skill_data.get('matched_skills', [])
                flat_match['missing_skills'] = skill_data.get('missing_skills', [])
                flat_match['skill_match_score'] = skill_data.get('skill_match_score', 0.0)
            
            # Save the flattened record
            match_id = self.save_match(flat_match)
            match_ids.append(match_id)
        
        return match_ids
    
    def load_history(self) -> List[Dict]:
        """Load all match history"""
        return self._load_from_file()
    
    def get_by_decision(self, decision: str) -> List[Dict]:
        """
        Get matches filtered by decision type
        
        Args:
            decision: 'SHORTLIST', 'REVIEW', or 'REJECT'
            
        Returns:
            List of matches with specified decision
        """
        history = self._load_from_file()
        return [m for m in history if m.get('decision') == decision]
    
    def get_statistics(self) -> Dict:
        """
        Calculate statistics from match history
        
        Returns:
            Dictionary with various statistics
        """
        history = self._load_from_file()
        
        if not history:
            return {
                'total_matches': 0,
                'shortlist_count': 0,
                'review_count': 0,
                'reject_count': 0,
                'avg_confidence': 0.0,
                'avg_skill_match': 0.0,
                'avg_experience_match': 0.0
            }
        
        shortlist = [m for m in history if m.get('decision') == 'SHORTLIST']
        review = [m for m in history if m.get('decision') == 'REVIEW']
        reject = [m for m in history if m.get('decision') == 'REJECT']
        
        confidences = [m.get('confidence', 0) for m in history]
        skill_scores = [m.get('skill_match_score', 0) for m in history]
        exp_scores = [m.get('experience_match_score', 0) for m in history]
        
        return {
            'total_matches': len(history),
            'shortlist_count': len(shortlist),
            'review_count': len(review),
            'reject_count': len(reject),
            'avg_confidence': sum(confidences) / len(confidences) if confidences else 0,
            'avg_skill_match': sum(skill_scores) / len(skill_scores) if skill_scores else 0,
            'avg_ats_score': sum([m.get('ats_score', 0) for m in history]) / len(history) if history else 0,
            'avg_experience_match': sum(exp_scores) / len(exp_scores) if exp_scores else 0
        }
    
    def get_top_missing_skills(self, top_n: int = 10) -> List[tuple]:
        """
        Get most frequently missing skills
        
        Args:
            top_n: Number of top skills to return
            
        Returns:
            List of (skill, count) tuples
        """
        history = self._load_from_file()
        skill_counts = {}
        
        for match in history:
            for skill in match.get('missing_skills', []):
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Sort by count
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_skills[:top_n]
    
    def get_top_matched_skills(self, top_n: int = 10) -> List[tuple]:
        """
        Get most frequently matched skills
        
        Args:
            top_n: Number of top skills to return
            
        Returns:
            List of (skill, count) tuples
        """
        history = self._load_from_file()
        skill_counts = {}
        
        for match in history:
            for skill in match.get('matched_skills', []):
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Sort by count
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_skills[:top_n]
    
    def clear_history(self):
        """Clear all match history"""
        self._save_to_file([])
