"""
Parse search results into candidate dictionaries with enriched data
"""
import re
import json
from typing import List, Dict, Optional
from datetime import datetime
import config

class CandidateParser:
    def __init__(self):
        self.skill_patterns = {
            'programming': [
                'python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'swift', 'kotlin',
                'typescript', 'php', 'ruby', 'scala', 'r', 'matlab', 'perl', 'bash', 'shell'
            ],
            'frameworks': [
                'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring',
                'laravel', 'rails', 'asp.net', 'fastapi', 'gin', 'echo', 'koa'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
                'dynamodb', 'sqlite', 'oracle', 'sql server', 'neo4j', 'influxdb'
            ],
            'cloud': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible',
                'jenkins', 'gitlab', 'github actions', 'circleci', 'travis ci'
            ],
            'ml_ai': [
                'machine learning', 'deep learning', 'ai', 'artificial intelligence',
                'tensorflow', 'pytorch', 'scikit-learn', 'keras', 'opencv', 'numpy',
                'pandas', 'matplotlib', 'seaborn', 'jupyter', 'spark', 'hadoop'
            ],
            'mobile': [
                'ios', 'android', 'react native', 'flutter', 'xamarin', 'swift',
                'kotlin', 'objective-c', 'xcode', 'android studio'
            ]
        }
    
    def parse_candidates(self, raw_profiles: List[Dict], job_description: str) -> List[Dict]:
        """
        Parse and enrich candidate data from raw LinkedIn profiles
        """
        enriched_candidates = []
        
        for profile in raw_profiles:
            try:
                enriched = self._enrich_candidate_data(profile, job_description)
                if enriched:
                    enriched_candidates.append(enriched)
            except Exception as e:
                print(f"Error parsing candidate {profile.get('name', 'Unknown')}: {e}")
                continue
        
        return enriched_candidates
    
    def _enrich_candidate_data(self, profile: Dict, job_description: str) -> Optional[Dict]:
        """
        Enrich candidate data with extracted information
        """
        name = profile.get('name', 'Unknown')
        headline = profile.get('headline', '')
        location = profile.get('location', 'Unknown')
        linkedin_url = profile.get('linkedin_url', '')
        
        if not linkedin_url:
            return None
        
        # Extract skills from headline and job description
        skills = self._extract_skills(headline, job_description)
        
        # Extract experience level
        experience_level = self._determine_experience_level(headline)
        
        # Extract education hints
        education = self._extract_education_hints(headline)
        
        # Extract company information
        companies = self._extract_companies(headline)
        
        # Calculate tenure estimate
        tenure_estimate = self._estimate_tenure(headline)
        
        # Determine career trajectory
        trajectory = self._analyze_career_trajectory(headline, companies)
        
        enriched_candidate = {
            'name': name,
            'linkedin_url': linkedin_url,
            'headline': headline,
            'location': location,
            'skills': skills,
            'experience_level': experience_level,
            'education': education,
            'companies': companies,
            'tenure_estimate': tenure_estimate,
            'career_trajectory': trajectory,
            'confidence': profile.get('confidence', 0.7),
            'parsed_at': datetime.now().isoformat()
        }
        
        return enriched_candidate
    
    def _extract_skills(self, headline: str, job_description: str) -> List[str]:
        """
        Extract skills from headline and job description
        """
        skills = []
        text_lower = (headline + ' ' + job_description).lower()
        
        for category, skill_list in self.skill_patterns.items():
            for skill in skill_list:
                if skill in text_lower:
                    skills.append(skill)
        
        # Remove duplicates and return top skills
        unique_skills = list(set(skills))
        return unique_skills[:10]  # Limit to top 10 skills
    
    def _determine_experience_level(self, headline: str) -> str:
        """
        Determine experience level based on headline keywords
        """
        headline_lower = headline.lower()
        
        # Senior level indicators
        senior_indicators = ['senior', 'lead', 'principal', 'staff', 'architect', 'director', 'manager']
        for indicator in senior_indicators:
            if indicator in headline_lower:
                return 'senior'
        
        # Mid level indicators
        mid_indicators = ['software engineer', 'developer', 'engineer', 'programmer']
        for indicator in mid_indicators:
            if indicator in headline_lower:
                return 'mid'
        
        # Junior level indicators
        junior_indicators = ['junior', 'entry', 'associate', 'intern', 'graduate']
        for indicator in junior_indicators:
            if indicator in headline_lower:
                return 'junior'
        
        return 'unknown'
    
    def _extract_education_hints(self, headline: str) -> List[str]:
        """
        Extract education hints from headline
        """
        education_keywords = [
            'phd', 'doctorate', 'masters', 'ms', 'ma', 'bachelors', 'bs', 'ba',
            'computer science', 'cs', 'engineering', 'mathematics', 'statistics'
        ]
        
        found_education = []
        headline_lower = headline.lower()
        
        for keyword in education_keywords:
            if keyword in headline_lower:
                found_education.append(keyword)
        
        return found_education
    
    def _extract_companies(self, headline: str) -> List[str]:
        """
        Extract company names from headline
        """
        # Common tech companies
        tech_companies = [
            'google', 'microsoft', 'apple', 'amazon', 'meta', 'facebook', 'netflix',
            'uber', 'lyft', 'airbnb', 'twitter', 'linkedin', 'salesforce', 'oracle',
            'ibm', 'intel', 'nvidia', 'amd', 'cisco', 'vmware', 'adobe', 'paypal',
            'stripe', 'square', 'zoom', 'slack', 'dropbox', 'box', 'atlassian'
        ]
        
        found_companies = []
        headline_lower = headline.lower()
        
        for company in tech_companies:
            if company in headline_lower:
                found_companies.append(company)
        
        return found_companies
    
    def _estimate_tenure(self, headline: str) -> str:
        """
        Estimate tenure based on headline keywords
        """
        headline_lower = headline.lower()
        
        # Long tenure indicators
        long_tenure = ['senior', 'lead', 'principal', 'staff', 'architect', 'director']
        for indicator in long_tenure:
            if indicator in headline_lower:
                return '5+ years'
        
        # Medium tenure indicators
        medium_tenure = ['software engineer', 'developer', 'engineer']
        for indicator in medium_tenure:
            if indicator in headline_lower:
                return '2-5 years'
        
        # Short tenure indicators
        short_tenure = ['junior', 'entry', 'associate', 'intern', 'graduate']
        for indicator in short_tenure:
            if indicator in headline_lower:
                return '0-2 years'
        
        return 'unknown'
    
    def _analyze_career_trajectory(self, headline: str, companies: List[str]) -> str:
        """
        Analyze career trajectory based on headline and companies
        """
        headline_lower = headline.lower()
        
        # Upward trajectory indicators
        if any(word in headline_lower for word in ['senior', 'lead', 'principal', 'staff']):
            return 'upward'
        
        # Stable trajectory indicators
        if any(word in headline_lower for word in ['engineer', 'developer', 'programmer']):
            return 'stable'
        
        # Early career indicators
        if any(word in headline_lower for word in ['junior', 'entry', 'associate', 'intern']):
            return 'early_career'
        
        return 'unknown'
    
    def validate_candidate_data(self, candidate: Dict) -> bool:
        """
        Validate that candidate has minimum required data
        """
        required_fields = ['name', 'linkedin_url', 'headline']
        
        for field in required_fields:
            if not candidate.get(field):
                return False
        
        # Validate LinkedIn URL format
        linkedin_url = candidate.get('linkedin_url', '')
        if not linkedin_url.startswith('https://linkedin.com/in/'):
            return False
        
        return True
    
    def get_candidate_summary(self, candidate: Dict) -> str:
        """
        Generate a summary of candidate information
        """
        name = candidate.get('name', 'Unknown')
        headline = candidate.get('headline', '')
        location = candidate.get('location', 'Unknown')
        skills = candidate.get('skills', [])
        companies = candidate.get('companies', [])
        
        summary_parts = [f"{name} - {headline}"]
        
        if location != 'Unknown':
            summary_parts.append(f"Location: {location}")
        
        if skills:
            summary_parts.append(f"Skills: {', '.join(skills[:5])}")
        
        if companies:
            summary_parts.append(f"Companies: {', '.join(companies)}")
        
        return " | ".join(summary_parts) 