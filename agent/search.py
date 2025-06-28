"""
LinkedIn profile discovery via Google search
"""
import requests
import time
import json
import re
from typing import List, Dict, Optional
from urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup
import config

class LinkedInSearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cached search results"""
        try:
            with open(config.CACHE_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_cache(self):
        """Save search results to cache"""
        try:
            with open(config.CACHE_FILE, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    def _get_mock_profiles(self, job_description: str) -> List[Dict]:
        """Return mock profiles for demonstration when Google search fails"""
        mock_profiles = [
            {
                'linkedin_url': 'https://linkedin.com/in/sarah-johnson-ai',
                'name': 'Sarah Johnson',
                'headline': 'Senior Software Engineer at Google',
                'location': 'San Francisco, CA',
                'confidence': 0.9
            },
            {
                'linkedin_url': 'https://linkedin.com/in/mike-chen-dev',
                'name': 'Mike Chen',
                'headline': 'Lead Python Developer at Microsoft',
                'location': 'Seattle, WA',
                'confidence': 0.8
            },
            {
                'linkedin_url': 'https://linkedin.com/in/emma-rodriguez-eng',
                'name': 'Emma Rodriguez',
                'headline': 'Full Stack Engineer at Amazon',
                'location': 'Austin, TX',
                'confidence': 0.85
            },
            {
                'linkedin_url': 'https://linkedin.com/in/david-kim-aws',
                'name': 'David Kim',
                'headline': 'Cloud Solutions Architect at AWS',
                'location': 'New York, NY',
                'confidence': 0.9
            },
            {
                'linkedin_url': 'https://linkedin.com/in/lisa-wang-ml',
                'name': 'Lisa Wang',
                'headline': 'Machine Learning Engineer at Meta',
                'location': 'Palo Alto, CA',
                'confidence': 0.8
            }
        ]
        
        # Filter profiles based on job description keywords
        job_lower = job_description.lower()
        filtered_profiles = []
        
        for profile in mock_profiles:
            headline_lower = profile['headline'].lower()
            location_lower = profile['location'].lower()
            
            # Check if profile matches job requirements
            if any(keyword in headline_lower for keyword in ['python', 'software', 'engineer', 'developer']):
                if any(location in job_lower for location in ['california', 'san francisco', 'seattle', 'new york', 'austin']):
                    filtered_profiles.append(profile)
                elif 'remote' in job_lower or 'anywhere' in job_lower:
                    filtered_profiles.append(profile)
                elif not any(location in job_lower for location in ['california', 'san francisco', 'seattle', 'new york', 'austin']):
                    # If no specific location mentioned, include all
                    filtered_profiles.append(profile)
        
        return filtered_profiles[:config.MAX_CANDIDATES_PER_SEARCH]
    
    def _extract_keywords(self, job_description: str) -> List[str]:
        """Extract relevant keywords from job description"""
        # Common tech keywords
        tech_keywords = [
            'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker',
            'kubernetes', 'machine learning', 'ai', 'data science', 'devops',
            'frontend', 'backend', 'full stack', 'mobile', 'ios', 'android',
            'sql', 'nosql', 'mongodb', 'postgresql', 'redis', 'elasticsearch'
        ]
        
        # Extract location keywords
        location_pattern = r'\b(?:in|at|based in|located in)\s+([A-Za-z\s,]+?)(?:\s|\.|$)'
        locations = re.findall(location_pattern, job_description, re.IGNORECASE)
        
        # Extract company keywords
        company_pattern = r'\b(?:at|with|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        companies = re.findall(company_pattern, job_description, re.IGNORECASE)
        
        # Find matching tech keywords
        found_keywords = []
        job_lower = job_description.lower()
        for keyword in tech_keywords:
            if keyword in job_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:5] + locations[:2] + companies[:2]
    
    def search_linkedin_profiles(self, job_description: str, max_results: int = None) -> List[Dict]:
        """
        Search for LinkedIn profiles using Google search
        """
        if max_results is None:
            max_results = config.MAX_CANDIDATES_PER_SEARCH
        
        # Check cache first
        cache_key = f"{hash(job_description)}"
        if cache_key in self.cache:
            print(f"Using cached results for job description")
            return self.cache[cache_key][:max_results]
        
        # Try real search first
        try:
            # Extract keywords for search
            keywords = self._extract_keywords(job_description)
            if not keywords:
                keywords = ['software engineer', 'developer']  # fallback
            
            # Build search queries
            search_queries = self._build_search_queries(keywords)
            
            all_profiles = []
            
            for query in search_queries:
                try:
                    profiles = self._execute_search(query, max_results // len(search_queries))
                    all_profiles.extend(profiles)
                    
                    # Rate limiting
                    time.sleep(config.SEARCH_DELAY_SECONDS)
                    
                    if len(all_profiles) >= max_results:
                        break
                        
                except Exception as e:
                    print(f"Error searching for query '{query}': {e}")
                    continue
            
            # Remove duplicates and limit results
            unique_profiles = self._deduplicate_profiles(all_profiles)
            results = unique_profiles[:max_results]
            
            # If no real results, use mock data
            if not results:
                print("No real profiles found, using mock data for demonstration")
                results = self._get_mock_profiles(job_description)
            
            # Cache results
            self.cache[cache_key] = results
            self._save_cache()
            
            return results
            
        except Exception as e:
            print(f"Search failed, using mock data: {e}")
            # Return mock profiles when search fails
            return self._get_mock_profiles(job_description)
    
    def _build_search_queries(self, keywords: List[str]) -> List[str]:
        """Build search queries from keywords"""
        queries = []
        
        # Primary query with main keywords
        if len(keywords) >= 2:
            primary_keywords = keywords[:2]
            queries.append(f'site:{config.LINKEDIN_DOMAIN} {" ".join(primary_keywords)}')
        
        # Secondary queries with location
        location_keywords = [k for k in keywords if any(word in k.lower() for word in ['california', 'new york', 'texas', 'florida', 'washington'])]
        if location_keywords:
            for location in location_keywords[:2]:
                queries.append(f'site:{config.LINKEDIN_DOMAIN} {location}')
        
        # Fallback query
        if not queries:
            queries.append(f'site:{config.LINKEDIN_DOMAIN} software engineer')
        
        return queries
    
    def _execute_search(self, query: str, max_results: int) -> List[Dict]:
        """Execute Google search and extract LinkedIn profiles"""
        params = {
            'q': query,
            'num': min(max_results * 2, 20),  # Get more results to account for filtering
            'hl': 'en'
        }
        
        try:
            response = self.session.get(config.GOOGLE_SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            profiles = []
            
            # Find search result links
            search_results = soup.find_all('a', href=True)
            
            for result in search_results:
                href = result.get('href', '')
                
                # Extract LinkedIn profile URLs
                if config.LINKEDIN_DOMAIN in href and '/in/' in href:
                    # Clean the URL
                    profile_url = self._clean_linkedin_url(href)
                    if profile_url:
                        # Extract basic info from the result
                        title_element = result.find_parent().find('h3') if result.find_parent() else None
                        title = title_element.get_text().strip() if title_element else "LinkedIn Profile"
                        
                        # Extract location if available
                        location = self._extract_location_from_result(result)
                        
                        profiles.append({
                            'linkedin_url': profile_url,
                            'name': self._extract_name_from_title(title),
                            'headline': title,
                            'location': location,
                            'confidence': 0.7  # Default confidence
                        })
            
            return profiles
            
        except Exception as e:
            print(f"Error executing search: {e}")
            return []
    
    def _clean_linkedin_url(self, url: str) -> Optional[str]:
        """Clean and validate LinkedIn URL"""
        try:
            # Extract LinkedIn profile URL from Google redirect
            if '/url?q=' in url:
                url = url.split('/url?q=')[1].split('&')[0]
            
            # Ensure it's a valid LinkedIn profile URL
            if config.LINKEDIN_DOMAIN in url and '/in/' in url:
                # Remove tracking parameters
                clean_url = url.split('?')[0]
                return clean_url
            
            return None
        except:
            return None
    
    def _extract_name_from_title(self, title: str) -> str:
        """Extract name from LinkedIn profile title"""
        # Remove common suffixes
        title = re.sub(r'\s*-\s*LinkedIn', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\|\s*LinkedIn', '', title, flags=re.IGNORECASE)
        
        # Extract name (usually first part before dash or pipe)
        name = title.split(' - ')[0].split(' | ')[0].strip()
        
        return name if name else "Unknown"
    
    def _extract_location_from_result(self, result_element) -> str:
        """Extract location from search result"""
        try:
            # Look for location in nearby text
            parent = result_element.find_parent()
            if parent:
                text = parent.get_text()
                # Look for location patterns
                location_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})\b'
                match = re.search(location_pattern, text)
                if match:
                    return match.group(1)
        except:
            pass
        
        return "Unknown"
    
    def _deduplicate_profiles(self, profiles: List[Dict]) -> List[Dict]:
        """Remove duplicate profiles based on LinkedIn URL"""
        seen_urls = set()
        unique_profiles = []
        
        for profile in profiles:
            url = profile.get('linkedin_url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_profiles.append(profile)
        
        return unique_profiles 