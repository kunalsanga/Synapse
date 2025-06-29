"""
Enhanced Fit Score Logic for Synapse Hackathon
Follows the exact scoring rubric provided in the challenge
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
        
        # Hackathon scoring weights (exact from requirements)
        self.weights = {
            'education': 0.20,      # 20%
            'trajectory': 0.20,     # 20%
            'company': 0.15,        # 15%
            'skills': 0.25,         # 25% (experience match)
            'location': 0.10,       # 10%
            'tenure': 0.10          # 10%
        }
        
        # Elite schools for education scoring
        self.elite_schools = {
            'mit', 'stanford', 'harvard', 'caltech', 'berkeley', 'uc berkeley',
            'carnegie mellon', 'cmu', 'princeton', 'yale', 'columbia', 'upenn',
            'cornell', 'brown', 'dartmouth', 'duke', 'northwestern', 'georgia tech',
            'gatech', 'university of michigan', 'ucla', 'usc', 'university of illinois',
            'uiuc', 'university of texas', 'ut austin', 'university of washington',
            'uw', 'university of wisconsin', 'university of maryland', 'umd'
        }
        
        # Top tech companies for company scoring
        self.top_tech_companies = {
            'google', 'alphabet', 'microsoft', 'apple', 'amazon', 'meta', 'facebook',
            'netflix', 'tesla', 'nvidia', 'intel', 'amd', 'oracle', 'salesforce',
            'adobe', 'paypal', 'stripe', 'square', 'airbnb', 'uber', 'lyft',
            'twitter', 'linkedin', 'github', 'spotify', 'slack', 'zoom', 'dropbox',
            'palantir', 'databricks', 'snowflake', 'mongodb', 'elastic', 'confluent',
            'hashicorp', 'gitlab', 'atlassian', 'jira', 'confluence', 'notion',
            'figma', 'canva', 'discord', 'twitch', 'roblox', 'unity', 'epic games'
        }
    
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
        Score a single candidate using enhanced rule-based scoring
        """
        # Get rule-based scoring (more reliable for hackathon)
        score_breakdown = self._get_enhanced_rule_based_scores(candidate, job_description)
        
        # Calculate weighted fit score
        fit_score = self._calculate_weighted_score(score_breakdown)
        
        # Add scores to candidate
        candidate['fit_score'] = fit_score
        candidate['score_breakdown'] = score_breakdown
        
        return candidate
    
    def _get_enhanced_rule_based_scores(self, candidate: Dict, job_description: str) -> Dict:
        """
        Enhanced rule-based scoring following hackathon rubric exactly
        """
        scores = {}
        
        # Education score (20%)
        scores['education'] = self._score_education_enhanced(candidate, job_description)
        
        # Career trajectory score (20%)
        scores['trajectory'] = self._score_trajectory_enhanced(candidate, job_description)
        
        # Company relevance score (15%)
        scores['company'] = self._score_company_relevance_enhanced(candidate, job_description)
        
        # Skills/Experience match score (25%)
        scores['skills'] = self._score_skills_match_enhanced(candidate, job_description)
        
        # Location match score (10%)
        scores['location'] = self._score_location_match_enhanced(candidate, job_description)
        
        # Tenure score (10%)
        scores['tenure'] = self._score_tenure_enhanced(candidate, job_description)
        
        return scores
    
    def _score_education_enhanced(self, candidate: Dict, job_description: str) -> float:
        """
        Enhanced education scoring (20% weight)
        - Elite schools (MIT, Stanford, etc.): 9-10
        - Strong schools: 7-8
        - Standard universities: 5-6
        - Clear progression: 8-10
        """
        education = ' '.join(candidate.get('education', [])).lower()
        job_lower = job_description.lower()
        
        # Check for elite schools
        if any(school in education for school in self.elite_schools):
            return 9.5
        
        # Check for advanced degrees
        if any(degree in education for degree in ['phd', 'doctorate', 'ph.d']):
            return 9.0
        elif any(degree in education for degree in ['masters', 'ms', 'ma', 'm.s', 'm.a']):
            return 8.0
        elif any(degree in education for degree in ['bachelors', 'bs', 'ba', 'b.s', 'b.a']):
            return 7.0
        
        # Check for relevant technical fields
        tech_fields = ['computer science', 'cs', 'engineering', 'mathematics', 'statistics', 
                      'data science', 'machine learning', 'artificial intelligence', 'ai',
                      'software engineering', 'information technology', 'it']
        if any(field in education for field in tech_fields):
            return 8.0
        
        # Check for business/management fields (relevant for some roles)
        business_fields = ['business', 'management', 'economics', 'finance', 'mba']
        if any(field in education for field in business_fields):
            return 6.0
        
        # Check if job requires specific education
        if any(word in job_lower for word in ['phd', 'doctorate', 'masters', 'degree required']):
            return 4.0  # Lower score if education is required but not found
        
        return 5.0  # Default score for standard universities
    
    def _score_trajectory_enhanced(self, candidate: Dict, job_description: str) -> float:
        """
        Enhanced career trajectory scoring (20% weight)
        - Steady growth: 6-8
        - Limited progression: 3-5
        """
        companies = candidate.get('companies', [])
        experience_level = candidate.get('experience_level', 'unknown').lower()
        headline = candidate.get('headline', '').lower()
        
        # Check for upward progression in titles
        senior_titles = ['senior', 'lead', 'principal', 'staff', 'architect', 'director', 'manager', 'head']
        junior_titles = ['junior', 'associate', 'entry', 'graduate', 'intern']
        
        senior_count = sum(1 for title in senior_titles if title in headline)
        junior_count = sum(1 for title in junior_titles if title in headline)
        
        # More senior titles indicate better trajectory
        if senior_count > junior_count:
            return 8.0
        elif senior_count == junior_count:
            return 6.0
        else:
            return 4.0
    
    def _score_company_relevance_enhanced(self, candidate: Dict, job_description: str) -> float:
        """
        Enhanced company relevance scoring (15% weight)
        - Top tech companies: 9-10
        - Relevant industry: 7-8
        - Any experience: 5-6
        """
        companies = ' '.join(candidate.get('companies', [])).lower()
        job_lower = job_description.lower()
        
        # Check for top tech companies
        if any(company in companies for company in self.top_tech_companies):
            return 9.5
        
        # Check for relevant industry keywords
        industry_keywords = {
            'fintech': ['fintech', 'financial', 'banking', 'payments', 'stripe', 'paypal', 'square'],
            'ai/ml': ['ai', 'machine learning', 'ml', 'artificial intelligence', 'deep learning'],
            'cloud': ['aws', 'azure', 'gcp', 'cloud', 'kubernetes', 'docker'],
            'startup': ['startup', 'venture', 'funded', 'series a', 'series b'],
            'enterprise': ['enterprise', 'saas', 'b2b', 'enterprise software']
        }
        
        # Extract industry from job description
        job_industry = None
        for industry, keywords in industry_keywords.items():
            if any(keyword in job_lower for keyword in keywords):
                job_industry = industry
                break
        
        # Check if candidate has relevant industry experience
        if job_industry and any(keyword in companies for keyword in industry_keywords[job_industry]):
            return 8.0
        
        # Check for any tech company experience
        tech_indicators = ['software', 'tech', 'technology', 'digital', 'online', 'web', 'app']
        if any(indicator in companies for indicator in tech_indicators):
            return 7.0
        
        return 5.0  # Default for any experience
    
    def _score_skills_match_enhanced(self, candidate: Dict, job_description: str) -> float:
        """
        Enhanced skills/experience match scoring (25% weight)
        - Perfect skill match: 9-10
        - Strong overlap: 7-8
        - Some relevant skills: 5-6
        """
        skills = ' '.join(candidate.get('skills', [])).lower()
        headline = candidate.get('headline', '').lower()
        job_lower = job_description.lower()
        
        # Extract key skills from job description
        job_skills = self._extract_skills_from_job_description(job_description)
        
        if not job_skills:
            return 5.0  # Default if no skills found
        
        # Count matching skills
        matches = 0
        for skill in job_skills:
            if skill in skills or skill in headline:
                matches += 1
        
        # Calculate match percentage
        match_percentage = matches / len(job_skills)
        
        if match_percentage >= 0.8:
            return 9.5  # Perfect match
        elif match_percentage >= 0.6:
            return 8.0  # Strong overlap
        elif match_percentage >= 0.4:
            return 7.0  # Good overlap
        elif match_percentage >= 0.2:
            return 6.0  # Some relevant skills
        else:
            return 4.0  # Poor match
    
    def _extract_skills_from_job_description(self, job_description: str) -> List[str]:
        """
        Extract key skills from job description
        """
        job_lower = job_description.lower()
        
        # Common tech skills
        tech_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'django', 'flask', 'fastapi', 'spring', 'express', 'ruby',
            'go', 'rust', 'c++', 'c#', '.net', 'php', 'sql', 'postgresql', 'mysql',
            'mongodb', 'redis', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'terraform', 'jenkins', 'git', 'github', 'gitlab', 'ci/cd', 'agile',
            'scrum', 'machine learning', 'ml', 'ai', 'deep learning', 'tensorflow',
            'pytorch', 'scikit-learn', 'pandas', 'numpy', 'spark', 'hadoop',
            'kafka', 'elasticsearch', 'microservices', 'api', 'rest', 'graphql',
            'frontend', 'backend', 'full stack', 'devops', 'data science'
        ]
        
        found_skills = []
        for skill in tech_skills:
            if skill in job_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _score_location_match_enhanced(self, candidate: Dict, job_description: str) -> float:
        """
        Enhanced location match scoring (10% weight)
        - Exact city: 10
        - Same metro: 8
        - Remote-friendly: 6
        """
        location = candidate.get('location', '').lower()
        job_lower = job_description.lower()
        
        # Extract location from job description
        job_location = self._extract_location_from_job_description(job_description)
        
        if not job_location:
            return 6.0  # Default for remote-friendly
        
        # Check for exact city match
        if job_location in location:
            return 10.0
        
        # Check for same metro area
        metro_areas = {
            'san francisco': ['sf', 'bay area', 'silicon valley', 'palo alto', 'mountain view', 'san mateo'],
            'new york': ['nyc', 'manhattan', 'brooklyn', 'queens', 'new jersey', 'nj'],
            'seattle': ['bellevue', 'redmond', 'kirkland', 'washington'],
            'austin': ['texas', 'tx'],
            'boston': ['cambridge', 'somerville', 'massachusetts', 'ma'],
            'los angeles': ['la', 'santa monica', 'culver city', 'california', 'ca']
        }
        
        for metro, cities in metro_areas.items():
            if metro in job_location and any(city in location for city in cities):
                return 8.0
            if any(city in job_location for city in cities) and any(city in location for city in cities):
                return 8.0
        
        # Check for remote-friendly indicators
        if any(word in job_lower for word in ['remote', 'work from home', 'wfh', 'anywhere']):
            return 6.0
        
        return 4.0  # Poor location match
    
    def _extract_location_from_job_description(self, job_description: str) -> str:
        """
        Extract location from job description
        """
        job_lower = job_description.lower()
        
        # Common tech hubs
        locations = [
            'san francisco', 'new york', 'seattle', 'austin', 'boston', 'los angeles',
            'chicago', 'denver', 'atlanta', 'miami', 'dallas', 'houston', 'phoenix',
            'portland', 'nashville', 'salt lake city', 'minneapolis', 'detroit'
        ]
        
        for location in locations:
            if location in job_lower:
                return location
        
        return ''
    
    def _score_tenure_enhanced(self, candidate: Dict, job_description: str) -> float:
        """
        Enhanced tenure scoring (10% weight)
        - 2-3 years average: 9-10
        - 1-2 years: 6-8
        - Job hopping: 3-5
        """
        companies = candidate.get('companies', [])
        experience_years = candidate.get('experience_years', 0)
        
        # Count companies to detect job hopping
        company_count = len(companies) if companies else 1
        
        # Calculate average tenure
        if company_count > 0:
            avg_tenure = experience_years / company_count
        else:
            avg_tenure = experience_years
        
        # Score based on tenure patterns
        if avg_tenure >= 2.0 and avg_tenure <= 3.0:
            return 9.5  # Ideal tenure
        elif avg_tenure >= 1.5 and avg_tenure < 2.0:
            return 8.0  # Good tenure
        elif avg_tenure >= 1.0 and avg_tenure < 1.5:
            return 7.0  # Acceptable tenure
        elif avg_tenure >= 0.5 and avg_tenure < 1.0:
            return 6.0  # Short tenure
        elif company_count > 3 and avg_tenure < 1.0:
            return 3.0  # Job hopping
        else:
            return 5.0  # Default
    
    def _calculate_weighted_score(self, score_breakdown: Dict) -> float:
        """
        Calculate weighted fit score based on hackathon rubric
        """
        total_score = 0.0
        
        for category, weight in self.weights.items():
            score = score_breakdown.get(category, 5.0)
            total_score += score * weight
        
        return round(total_score, 2)
    
    def get_score_explanation(self, candidate: Dict) -> str:
        """
        Generate explanation for candidate's score
        """
        breakdown = candidate.get('score_breakdown', {})
        fit_score = candidate.get('fit_score', 0)
        
        explanation = f"Overall Fit Score: {fit_score}/10\n\n"
        explanation += "Score Breakdown:\n"
        
        for category, score in breakdown.items():
            weight = self.weights.get(category, 0) * 100
            explanation += f"- {category.title()} ({weight}%): {score}/10\n"
        
        return explanation 