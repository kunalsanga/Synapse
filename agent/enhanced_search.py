"""
Enhanced LinkedIn profile discovery with multiple search providers
"""
import requests
import time
import json
import re
from typing import List, Dict, Optional
from urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup
import config
import os

class EnhancedLinkedInSearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })
        self.cache = self._load_cache()
        self.search_client = config.get_search_client()
        
        if config.DEBUG:
            print(f"Initialized EnhancedLinkedInSearcher with {self.search_client} client")
    
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
    
    def search_linkedin_profiles(self, job_description: str, max_results: int = None) -> List[Dict]:
        """Search for LinkedIn profiles using the configured search provider"""
        if max_results is None:
            max_results = config.MAX_CANDIDATES_PER_SEARCH
        
        # Check cache first for exact match
        cache_key = f"{hash(job_description)}"
        if cache_key in self.cache:
            print(f"Using cached results for job description")
            cached_profiles = self.cache[cache_key][:max_results]
            # Check if cached profiles are real or demo
            if any(not any(demo_suffix in p.get('linkedin_url', '') for demo_suffix in ['-ai', '-dev', '-eng', '-aws', '-ml']) for p in cached_profiles):
                print("Found real profiles in cache")
                return cached_profiles
            else:
                print("Found demo profiles in cache, will try to get real profiles")
        
        # Try configured search provider
        try:
            if self.search_client == "serpapi":
                profiles = self._search_with_serpapi(job_description, max_results)
            else:
                profiles = self._search_with_google(job_description, max_results)
            
            # If no results, use real profiles from cache (unconditional fallback)
            if not profiles:
                print("Search failed, using real profiles from cache if available")
                real_profiles = self._get_real_profiles_from_cache(job_description)
                if real_profiles:
                    print(f"Using {len(real_profiles)} real profiles from cache as fallback")
                    # Cache these results for future use
                    self.cache[cache_key] = real_profiles
                    self._save_cache()
                    return real_profiles[:max_results]
                else:
                    print("No real profiles in cache, using demo profiles")
                    profiles = self._get_mock_profiles(job_description)
            
            # Cache results
            self.cache[cache_key] = profiles
            self._save_cache()
            
            return profiles[:max_results]
            
        except Exception as e:
            print(f"Search failed: {e}")
            # Unconditional fallback to real profiles from cache
            real_profiles = self._get_real_profiles_from_cache(job_description)
            if real_profiles:
                print(f"Using {len(real_profiles)} real profiles from cache after search failure")
                return real_profiles[:max_results]
            else:
                print("No real profiles available, using demo profiles")
                return self._get_mock_profiles(job_description)
    
    def _search_with_serpapi(self, job_description: str, max_results: int) -> List[Dict]:
        """Search using SerpAPI (most reliable)"""
        if not config.SERPAPI_KEY:
            print("SerpAPI key not configured")
            return []
        
        keywords = self._extract_keywords(job_description)
        profiles = []
        
        for keyword in keywords[:3]:
            try:
                query = f'site:linkedin.com/in {keyword}'
                params = {
                    'q': query,
                    'api_key': config.SERPAPI_KEY,
                    'engine': 'google',
                    'num': min(max_results, 10)
                }
                
                response = self.session.get(config.SERPAPI_URL, params=params)
                response.raise_for_status()
                
                data = response.json()
                organic_results = data.get('organic_results', [])
                
                for result in organic_results:
                    profile = self._parse_serpapi_result(result)
                    if profile:
                        profiles.append(profile)
                
                time.sleep(config.SEARCH_DELAY_SECONDS)
                
            except Exception as e:
                print(f"SerpAPI search error for '{keyword}': {e}")
                continue
        
        return self._deduplicate_profiles(profiles)
    
    def _search_with_google(self, job_description: str, max_results: int) -> List[Dict]:
        """Search using Google (free but may be rate limited)"""
        keywords = self._extract_keywords(job_description)
        search_queries = self._build_search_queries(keywords)
        
        all_profiles = []
        
        for query in search_queries:
            try:
                profiles = self._execute_google_search(query, max_results // len(search_queries))
                all_profiles.extend(profiles)
                
                time.sleep(config.SEARCH_DELAY_SECONDS)
                
                if len(all_profiles) >= max_results:
                    break
                    
            except Exception as e:
                print(f"Google search error for '{query}': {e}")
                continue
        
        return self._deduplicate_profiles(all_profiles)[:max_results]
    
    def _execute_google_search(self, query: str, max_results: int) -> List[Dict]:
        """Execute Google search and extract LinkedIn profiles"""
        try:
            params = {
                'q': query,
                'num': min(max_results, 10)
            }
            
            response = self.session.get(config.GOOGLE_SEARCH_URL, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = soup.find_all('div', class_='g')
            
            profiles = []
            for result in search_results:
                profile = self._parse_google_result(result)
                if profile:
                    profiles.append(profile)
            
            return profiles
            
        except Exception as e:
            print(f"Google search execution error: {e}")
            return []
    
    def _parse_serpapi_result(self, result: Dict) -> Optional[Dict]:
        """Parse SerpAPI search result"""
        try:
            title = result.get('title', '')
            link = result.get('link', '')
            snippet = result.get('snippet', '')
            
            if not self._is_linkedin_profile_url(link):
                return None
            
            name = self._extract_name_from_title(title)
            location = self._extract_location_from_snippet(snippet)
            
            return {
                'linkedin_url': link,
                'name': name,
                'headline': title.replace(f"{name} - ", "").split(" | ")[0],
                'location': location,
                'confidence': 0.9
            }
            
        except Exception as e:
            print(f"Error parsing SerpAPI result: {e}")
            return None
    
    def _parse_google_result(self, result_element) -> Optional[Dict]:
        """Parse Google search result"""
        try:
            title_element = result_element.find('h3')
            link_element = result_element.find('a')
            
            if not title_element or not link_element:
                return None
            
            title = title_element.get_text()
            link = link_element.get('href', '')
            
            if not self._is_linkedin_profile_url(link):
                return None
            
            name = self._extract_name_from_title(title)
            location = self._extract_location_from_result(result_element)
            
            return {
                'linkedin_url': link,
                'name': name,
                'headline': title.replace(f"{name} - ", "").split(" | ")[0],
                'location': location,
                'confidence': 0.8
            }
            
        except Exception as e:
            print(f"Error parsing Google result: {e}")
            return None
    
    def _extract_keywords(self, job_description: str) -> List[str]:
        """Extract relevant keywords from job description"""
        tech_keywords = [
            'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker',
            'kubernetes', 'machine learning', 'ai', 'data science', 'devops',
            'frontend', 'backend', 'full stack', 'mobile', 'ios', 'android',
            'sql', 'nosql', 'mongodb', 'postgresql', 'redis', 'elasticsearch',
            'software engineer', 'developer', 'architect', 'manager', 'lead'
        ]
        
        location_pattern = r'\b(?:in|at|based in|located in)\s+([A-Za-z\s,]+?)(?:\s|\.|$)'
        locations = re.findall(location_pattern, job_description, re.IGNORECASE)
        
        company_pattern = r'\b(?:at|with|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        companies = re.findall(company_pattern, job_description, re.IGNORECASE)
        
        found_keywords = []
        job_lower = job_description.lower()
        for keyword in tech_keywords:
            if keyword in job_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:5] + locations[:2] + companies[:2]
    
    def _build_search_queries(self, keywords: List[str]) -> List[str]:
        """Build search queries from keywords"""
        queries = []
        
        if len(keywords) >= 2:
            primary_keywords = keywords[:2]
            queries.append(f'site:{config.LINKEDIN_DOMAIN} {" ".join(primary_keywords)}')
        
        location_keywords = [k for k in keywords if any(word in k.lower() for word in ['california', 'new york', 'texas', 'florida', 'washington', 'seattle', 'san francisco', 'austin'])]
        if location_keywords:
            for location in location_keywords[:2]:
                queries.append(f'site:{config.LINKEDIN_DOMAIN} {location}')
        
        if not queries:
            queries.append(f'site:{config.LINKEDIN_DOMAIN} software engineer')
        
        return queries
    
    def _is_linkedin_profile_url(self, url: str) -> bool:
        """Check if URL is a LinkedIn profile URL"""
        return config.LINKEDIN_DOMAIN in url and '/in/' in url
    
    def _extract_name_from_title(self, title: str) -> str:
        """Extract name from LinkedIn profile title"""
        title = re.sub(r'\s*-\s*.*$', '', title)
        title = re.sub(r'\s*\|\s*.*$', '', title)
        name = title.split(' - ')[0].split(' | ')[0].strip()
        name = re.sub(r'[^\w\s-]', '', name)
        return name
    
    def _extract_location_from_snippet(self, snippet: str) -> str:
        """Extract location from search result snippet"""
        location_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, snippet)
            if match:
                return match.group(1)
        
        return "Unknown"
    
    def _extract_location_from_result(self, result_element) -> str:
        """Extract location from Google search result"""
        try:
            snippet_element = result_element.find('span', class_='aCOpRe')
            if snippet_element:
                return self._extract_location_from_snippet(snippet_element.get_text())
            
            for element in result_element.find_all(['span', 'div']):
                text = element.get_text()
                if any(location in text.lower() for location in ['california', 'new york', 'texas', 'florida', 'washington']):
                    return self._extract_location_from_snippet(text)
            
            return "Unknown"
        except:
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
    
    def _get_mock_profiles(self, job_description: str) -> List[Dict]:
        """Return real profiles from cache or mock profiles as fallback"""
        # First, try to get real profiles from cache
        real_profiles = self._get_real_profiles_from_cache(job_description)
        if real_profiles:
            print(f"Using {len(real_profiles)} real profiles from cache")
            return real_profiles
        
        # Fallback to mock profiles if no real profiles found
        print("No real profiles found in cache, using demo profiles")
        mock_profiles = [
            {
                'linkedin_url': 'https://www.linkedin.com/in/sarah-johnson-ai',
                'name': 'Sarah Johnson',
                'headline': 'Senior Software Engineer at Google',
                'location': 'San Francisco, CA',
                'confidence': 0.9
            },
            {
                'linkedin_url': 'https://www.linkedin.com/in/mike-chen-dev',
                'name': 'Mike Chen',
                'headline': 'Lead Python Developer at Microsoft',
                'location': 'Seattle, WA',
                'confidence': 0.8
            },
            {
                'linkedin_url': 'https://www.linkedin.com/in/emma-rodriguez-eng',
                'name': 'Emma Rodriguez',
                'headline': 'Full Stack Engineer at Amazon',
                'location': 'Austin, TX',
                'confidence': 0.85
            },
            {
                'linkedin_url': 'https://www.linkedin.com/in/david-kim-aws',
                'name': 'David Kim',
                'headline': 'Cloud Solutions Architect at AWS',
                'location': 'New York, NY',
                'confidence': 0.9
            },
            {
                'linkedin_url': 'https://www.linkedin.com/in/lisa-wang-ml',
                'name': 'Lisa Wang',
                'headline': 'Machine Learning Engineer at Meta',
                'location': 'Palo Alto, CA',
                'confidence': 0.8
            }
        ]
        
        job_lower = job_description.lower()
        filtered_profiles = []
        
        for profile in mock_profiles:
            headline_lower = profile['headline'].lower()
            location_lower = profile['location'].lower()
            
            if any(keyword in headline_lower for keyword in ['python', 'software', 'engineer', 'developer', 'architect']):
                if any(location in job_lower for location in ['california', 'san francisco', 'seattle', 'new york', 'austin', 'palo alto']):
                    filtered_profiles.append(profile)
                elif 'remote' in job_lower or 'anywhere' in job_lower:
                    filtered_profiles.append(profile)
                elif not any(location in job_lower for location in ['california', 'san francisco', 'seattle', 'new york', 'austin', 'palo alto']):
                    filtered_profiles.append(profile)
        
        return filtered_profiles[:config.MAX_CANDIDATES_PER_SEARCH]
    
    def _get_real_profiles_from_cache(self, job_description: str = None) -> List[Dict]:
        """Return all real profiles from cache, no filtering or scoring. Always reload cache from disk."""
        try:
            # Always reload cache from disk to ensure up-to-date data
            cache_path = os.path.join(os.path.dirname(__file__), 'cache.json')
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
            if not self.cache:
                return []
            real_profiles = []
            for cache_key, profiles in self.cache.items():
                for profile in profiles:
                    if (isinstance(profile, dict) and 
                        'linkedin_url' in profile and 
                        not any(demo_suffix in profile['linkedin_url'] for demo_suffix in ['-ai', '-dev', '-eng', '-aws', '-ml'])):
                        real_profiles.append(profile)
            print(f"[CACHE FALLBACK] Returning {len(real_profiles)} real profiles from cache (no filtering)")
            return real_profiles[:config.MAX_CANDIDATES_PER_SEARCH]
        except Exception as e:
            print(f"Error getting real profiles from cache: {e}")
            return [] 