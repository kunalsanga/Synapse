"""
Fit score logic for candidate evaluation
"""
import re
import json
from typing import Dict, List, Tuple
import google.generativeai as genai
import config

class CandidateScorer:
    def __init__(self):
        self.gemini_client = None
        if config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.gemini_client = genai.GenerativeModel(config.GEMINI_MODEL)
        
        self.weights = config.FIT_SCORE_WEIGHTS
    
    def score_candidates(self, candidates: List[Dict], job_description: str) -> List[Dict]:
        """
        Score all candidates and return sorted results
        """
        scored_candidates = []
        
        for candidate in candidates:
            try:
                scored = self._score_single_candidate(candidate, job_description)
                if scored:
                    scored_candidates.append(scored)
            except Exception as e:
                print(f"Error scoring candidate {candidate.get('name', 'Unknown')}: {e}")
                # Add candidate with default low score
                candidate['fit_score'] = 1.0
                candidate['score_breakdown'] = {
                    'education': 1.0,
                    'trajectory': 1.0,
                    'company': 1.0,
                    'skills': 1.0,
                    'location': 1.0,
                    'tenure': 1.0
                }
                scored_candidates.append(candidate)
        
        # Sort by fit score (highest first)
        scored_candidates.sort(key=lambda x: x.get('fit_score', 0), reverse=True)
        
        return scored_candidates
    
    def _score_single_candidate(self, candidate: Dict, job_description: str) -> Dict:
        """
        Score a single candidate using AI and rule-based scoring
        """
        # Get AI-based scoring if available
        ai_scores = self._get_ai_scores(candidate, job_description)
        
        # Get rule-based scoring as fallback
        rule_scores = self._get_rule_based_scores(candidate, job_description)
        
        # Combine scores (prefer AI if available)
        if ai_scores:
            score_breakdown = ai_scores
        else:
            score_breakdown = rule_scores
        
        # Calculate weighted fit score
        fit_score = self._calculate_weighted_score(score_breakdown)
        
        # Add scores to candidate
        candidate['fit_score'] = fit_score
        candidate['score_breakdown'] = score_breakdown
        
        return candidate
    
    def _get_ai_scores(self, candidate: Dict, job_description: str) -> Dict:
        """
        Get AI-based scores using Gemini
        """
        if not self.gemini_client:
            return {}
        
        try:
            # Prepare candidate data for AI scoring
            name = candidate.get('name', 'Unknown')
            headline = candidate.get('headline', '')
            location = candidate.get('location', 'Unknown')
            skills = ', '.join(candidate.get('skills', []))
            companies = ', '.join(candidate.get('companies', []))
            education = ', '.join(candidate.get('education', []))
            
            experience_summary = f"{headline} at {companies}" if companies else headline
            
            prompt = config.SCORING_PROMPT_TEMPLATE.format(
                name=name,
                headline=headline,
                location=location,
                experience=experience_summary,
                job_description=job_description
            )
            
            response = self.gemini_client.generate_content(prompt)
            
            # Parse AI response
            ai_response = response.text
            scores = self._parse_ai_scoring_response(ai_response)
            
            return scores
            
        except Exception as e:
            print(f"AI scoring failed: {e}")
            return {}
    
    def _parse_ai_scoring_response(self, response: str) -> Dict:
        """
        Parse AI scoring response to extract scores
        """
        scores = {}
        
        # Look for score patterns in the response
        score_patterns = {
            'education': r'education[:\s]*(\d+(?:\.\d+)?)',
            'trajectory': r'trajectory[:\s]*(\d+(?:\.\d+)?)',
            'company': r'company[:\s]*(\d+(?:\.\d+)?)',
            'skills': r'(?:skills|experience)[:\s]*(\d+(?:\.\d+)?)',
            'location': r'location[:\s]*(\d+(?:\.\d+)?)',
            'tenure': r'tenure[:\s]*(\d+(?:\.\d+)?)'
        }
        
        for category, pattern in score_patterns.items():
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    scores[category] = min(max(score, 1.0), 10.0)  # Clamp between 1-10
                except ValueError:
                    scores[category] = 5.0  # Default score
            else:
                scores[category] = 5.0  # Default score
        
        return scores
    
    def _get_rule_based_scores(self, candidate: Dict, job_description: str) -> Dict:
        """
        Get rule-based scores as fallback when AI is not available
        """
        scores = {}
        
        # Education score
        scores['education'] = self._score_education(candidate, job_description)
        
        # Career trajectory score
        scores['trajectory'] = self._score_trajectory(candidate, job_description)
        
        # Company relevance score
        scores['company'] = self._score_company_relevance(candidate, job_description)
        
        # Skills/Experience match score
        scores['skills'] = self._score_skills_match(candidate, job_description)
        
        # Location match score
        scores['location'] = self._score_location_match(candidate, job_description)
        
        # Tenure score
        scores['tenure'] = self._score_tenure(candidate, job_description)
        
        return scores
    
    def _score_education(self, candidate: Dict, job_description: str) -> float:
        """
        Score education relevance (1-10)
        """
        education = candidate.get('education', [])
        job_lower = job_description.lower()
        
        # Check for advanced degrees
        if any(degree in education for degree in ['phd', 'doctorate']):
            return 9.0
        elif any(degree in education for degree in ['masters', 'ms', 'ma']):
            return 8.0
        elif any(degree in education for degree in ['bachelors', 'bs', 'ba']):
            return 7.0
        
        # Check for relevant fields
        relevant_fields = ['computer science', 'cs', 'engineering', 'mathematics', 'statistics']
        if any(field in education for field in relevant_fields):
            return 8.0
        
        # Check if job requires specific education
        if any(word in job_lower for word in ['phd', 'doctorate', 'masters', 'degree']):
            return 4.0  # Lower score if education is required but not found
        
        return 6.0  # Default score
    
    def _score_trajectory(self, candidate: Dict, job_description: str) -> float:
        """
        Score career trajectory (1-10)
        """
        trajectory = candidate.get('career_trajectory', 'unknown')
        experience_level = candidate.get('experience_level', 'unknown')
        
        # Upward trajectory is good
        if trajectory == 'upward':
            return 9.0
        elif trajectory == 'stable':
            return 7.0
        elif trajectory == 'early_career':
            return 6.0
        
        # Experience level scoring
        if experience_level == 'senior':
            return 8.0
        elif experience_level == 'mid':
            return 7.0
        elif experience_level == 'junior':
            return 5.0
        
        return 6.0
    
    def _score_company_relevance(self, candidate: Dict, job_description: str) -> float:
        """
        Score company relevance (1-10)
        """
        companies = candidate.get('companies', [])
        job_lower = job_description.lower()
        
        if not companies:
            return 5.0
        
        # Tier 1 companies (high score)
        tier1_companies = ['google', 'microsoft', 'apple', 'amazon', 'meta', 'netflix']
        if any(company in companies for company in tier1_companies):
            return 9.0
        
        # Tier 2 companies (good score)
        tier2_companies = ['uber', 'lyft', 'airbnb', 'twitter', 'linkedin', 'salesforce']
        if any(company in companies for company in tier2_companies):
            return 8.0
        
        # Check if job mentions specific companies
        for company in companies:
            if company.lower() in job_lower:
                return 8.5
        
        return 6.0
    
    def _score_skills_match(self, candidate: Dict, job_description: str) -> float:
        """
        Score skills/experience match (1-10)
        """
        skills = candidate.get('skills', [])
        job_lower = job_description.lower()
        
        if not skills:
            return 3.0
        
        # Count matching skills
        matching_skills = 0
        for skill in skills:
            if skill.lower() in job_lower:
                matching_skills += 1
        
        # Calculate score based on match percentage
        if len(skills) > 0:
            match_percentage = matching_skills / len(skills)
            return 3.0 + (match_percentage * 7.0)  # Scale from 3-10
        
        return 5.0
    
    def _score_location_match(self, candidate: Dict, job_description: str) -> float:
        """
        Score location match (1-10)
        """
        location = candidate.get('location', 'Unknown').lower()
        job_lower = job_description.lower()
        
        if location == 'unknown':
            return 5.0
        
        # Check for exact location matches
        if location in job_lower:
            return 10.0
        
        # Check for state/region matches
        states = ['california', 'new york', 'texas', 'florida', 'washington', 'massachusetts']
        for state in states:
            if state in location and state in job_lower:
                return 9.0
        
        # Check for remote work indicators
        if any(word in job_lower for word in ['remote', 'work from home', 'wfh']):
            return 8.0  # Good for remote positions
        
        return 6.0
    
    def _score_tenure(self, candidate: Dict, job_description: str) -> float:
        """
        Score tenure/stability (1-10)
        """
        tenure = candidate.get('tenure_estimate', 'unknown')
        job_lower = job_description.lower()
        
        if tenure == '5+ years':
            return 9.0
        elif tenure == '2-5 years':
            return 7.0
        elif tenure == '0-2 years':
            return 5.0
        
        # Check if job requires specific experience
        if any(word in job_lower for word in ['senior', 'lead', 'principal', '5+ years']):
            return 4.0  # Lower score for senior roles if tenure is unknown
        
        return 6.0
    
    def _calculate_weighted_score(self, score_breakdown: Dict) -> float:
        """
        Calculate weighted fit score from individual scores
        """
        total_score = 0.0
        
        for category, score in score_breakdown.items():
            weight = self.weights.get(category, 0.0)
            total_score += score * weight
        
        return round(total_score, 2)
    
    def get_score_explanation(self, candidate: Dict) -> str:
        """
        Generate explanation for candidate's score
        """
        score_breakdown = candidate.get('score_breakdown', {})
        fit_score = candidate.get('fit_score', 0)
        
        if not score_breakdown:
            return f"Overall fit score: {fit_score}/10"
        
        explanation_parts = [f"Overall fit score: {fit_score}/10"]
        
        # Add top strengths
        strengths = []
        for category, score in score_breakdown.items():
            if score >= 8.0:
                strengths.append(f"{category.title()} ({score})")
        
        if strengths:
            explanation_parts.append(f"Strengths: {', '.join(strengths)}")
        
        # Add areas for improvement
        improvements = []
        for category, score in score_breakdown.items():
            if score <= 5.0:
                improvements.append(f"{category.title()} ({score})")
        
        if improvements:
            explanation_parts.append(f"Areas for improvement: {', '.join(improvements)}")
        
        return " | ".join(explanation_parts) 