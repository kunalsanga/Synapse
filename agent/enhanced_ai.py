"""
Enhanced AI client supporting multiple providers
"""
import json
import time
from typing import Dict, List, Optional
import config

class EnhancedAIClient:
    def __init__(self):
        self.ai_client = config.get_ai_client()
        self.provider = config.AI_PROVIDER
        
        if config.DEBUG:
            print(f"Initialized EnhancedAIClient with {self.provider} provider")
    
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Generate text using the configured AI provider"""
        if not self.ai_client:
            print("No AI client available")
            return None
        
        try:
            if self.provider == "gemini":
                return self._generate_with_gemini(prompt, max_tokens)
            elif self.provider == "openai":
                return self._generate_with_openai(prompt, max_tokens)
            elif self.provider == "anthropic":
                return self._generate_with_anthropic(prompt, max_tokens)
            else:
                print(f"Unknown AI provider: {self.provider}")
                return None
                
        except Exception as e:
            print(f"AI generation error: {e}")
            return None
    
    def _generate_with_gemini(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Generate text using Google Gemini"""
        try:
            response = self.ai_client.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini generation error: {e}")
            return None
    
    def _generate_with_openai(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Generate text using OpenAI"""
        try:
            response = self.ai_client.ChatCompletion.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for LinkedIn candidate analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI generation error: {e}")
            return None
    
    def _generate_with_anthropic(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Generate text using Anthropic Claude"""
        try:
            response = self.ai_client.messages.create(
                model=config.ANTHROPIC_MODEL,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Anthropic generation error: {e}")
            return None
    
    def score_candidate(self, candidate: Dict, job_description: str) -> Dict:
        """Score a candidate using AI"""
        if not self.ai_client:
            return self._get_default_score()
        
        try:
            prompt = config.SCORING_PROMPT_TEMPLATE.format(
                name=candidate.get('name', 'Unknown'),
                headline=candidate.get('headline', 'Unknown'),
                location=candidate.get('location', 'Unknown'),
                experience=candidate.get('experience', 'Unknown'),
                job_description=job_description
            )
            
            response = self.generate_text(prompt, max_tokens=500)
            
            if response:
                return self._parse_scoring_response(response)
            else:
                return self._get_default_score()
                
        except Exception as e:
            print(f"Scoring error: {e}")
            return self._get_default_score()
    
    def generate_outreach_message(self, candidate: Dict, job_description: str) -> str:
        """Generate personalized outreach message"""
        if not self.ai_client:
            return self._get_default_message(candidate)
        
        try:
            prompt = config.OUTREACH_MESSAGE_TEMPLATE.format(
                name=candidate.get('name', 'there'),
                headline=candidate.get('headline', 'professional'),
                location=candidate.get('location', 'your area'),
                skills=candidate.get('skills', 'your background'),
                job_description=job_description
            )
            
            response = self.generate_text(prompt, max_tokens=300)
            
            if response:
                return response.strip()
            else:
                return self._get_default_message(candidate)
                
        except Exception as e:
            print(f"Message generation error: {e}")
            return self._get_default_message(candidate)
    
    def _parse_scoring_response(self, response: str) -> Dict:
        """Parse AI scoring response"""
        try:
            # Try to extract scores from response
            scores = {
                "education": 7.0,
                "trajectory": 7.0,
                "company": 7.0,
                "skills": 7.0,
                "location": 7.0,
                "tenure": 7.0
            }
            
            # Look for score patterns in response
            lines = response.lower().split('\n')
            for line in lines:
                for category in scores.keys():
                    if category in line:
                        # Extract number from line
                        import re
                        numbers = re.findall(r'\d+(?:\.\d+)?', line)
                        if numbers:
                            scores[category] = min(10.0, max(1.0, float(numbers[0])))
            
            return scores
            
        except Exception as e:
            print(f"Score parsing error: {e}")
            return self._get_default_score()
    
    def _get_default_score(self) -> Dict:
        """Get default scoring when AI is not available"""
        return {
            "education": 7.0,
            "trajectory": 7.0,
            "company": 7.0,
            "skills": 7.0,
            "location": 7.0,
            "tenure": 7.0
        }
    
    def _get_default_message(self, candidate: Dict) -> str:
        """Get default outreach message when AI is not available"""
        name = candidate.get('name', 'there')
        headline = candidate.get('headline', 'professional')
        
        return f"""Hi {name},

I came across your profile and was impressed by your background as a {headline}. I believe your experience would be a great fit for a role we're currently hiring for.

Would you be interested in learning more about this opportunity? I'd love to connect and discuss how your skills could contribute to our team.

Best regards,
[Your Name]"""
    
    def is_available(self) -> bool:
        """Check if AI client is available"""
        return self.ai_client is not None
    
    def get_provider_info(self) -> Dict:
        """Get information about the current AI provider"""
        return {
            "provider": self.provider,
            "available": self.is_available(),
            "model": self._get_model_name()
        }
    
    def _get_model_name(self) -> str:
        """Get the current model name"""
        if self.provider == "gemini":
            return config.GEMINI_MODEL
        elif self.provider == "openai":
            return config.OPENAI_MODEL
        elif self.provider == "anthropic":
            return config.ANTHROPIC_MODEL
        else:
            return "unknown" 