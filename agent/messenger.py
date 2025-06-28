"""
Gemini-based outreach message generator
"""
import re
import json
from typing import Dict, List, Optional
import google.generativeai as genai
import config

class MessageGenerator:
    def __init__(self):
        self.gemini_client = None
        if config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.gemini_client = genai.GenerativeModel(config.GEMINI_MODEL)
        
        self.message_templates = {
            'senior': {
                'tone': 'professional and respectful',
                'focus': 'leadership experience and strategic impact',
                'cta': 'schedule a call to discuss opportunities'
            },
            'mid': {
                'tone': 'friendly and collaborative',
                'focus': 'technical skills and growth potential',
                'cta': 'connect and explore potential opportunities'
            },
            'junior': {
                'tone': 'encouraging and supportive',
                'focus': 'learning potential and career growth',
                'cta': 'discuss career development opportunities'
            }
        }
    
    def generate_outreach_messages(self, candidates: List[Dict], job_description: str) -> List[Dict]:
        """
        Generate personalized outreach messages for all candidates
        """
        candidates_with_messages = []
        
        for candidate in candidates:
            try:
                message = self._generate_single_message(candidate, job_description)
                candidate['outreach_message'] = message
                candidates_with_messages.append(candidate)
            except Exception as e:
                print(f"Error generating message for {candidate.get('name', 'Unknown')}: {e}")
                # Add fallback message
                candidate['outreach_message'] = self._generate_fallback_message(candidate, job_description)
                candidates_with_messages.append(candidate)
        
        return candidates_with_messages
    
    def _generate_single_message(self, candidate: Dict, job_description: str) -> str:
        """
        Generate a personalized message for a single candidate
        """
        if not self.gemini_client:
            return self._generate_fallback_message(candidate, job_description)
        
        try:
            # Prepare candidate data
            name = candidate.get('name', 'there')
            headline = candidate.get('headline', '')
            location = candidate.get('location', '')
            skills = candidate.get('skills', [])
            companies = candidate.get('companies', [])
            experience_level = candidate.get('experience_level', 'mid')
            
            # Get message style based on experience level
            style = self.message_templates.get(experience_level, self.message_templates['mid'])
            
            # Create skills summary
            skills_summary = ', '.join(skills[:5]) if skills else 'your technical background'
            
            # Create company summary
            company_summary = ''
            if companies:
                if len(companies) == 1:
                    company_summary = f"your experience at {companies[0]}"
                else:
                    company_summary = f"your experience at companies like {', '.join(companies[:2])}"
            
            # Build prompt
            prompt = f"""
Generate a personalized LinkedIn outreach message for {name}, a {headline} based in {location}.

Key details:
- Skills: {skills_summary}
- Companies: {company_summary}
- Experience level: {experience_level}

Job description:
{job_description}

Message requirements:
- Tone: {style['tone']}
- Focus on: {style['focus']}
- Call-to-action: {style['cta']}
- Keep under 200 words
- Be specific to their background
- Avoid generic templates
- Start with a personalized greeting
- Reference their specific experience or skills
- End with a clear next step

Generate only the message text, no additional formatting.
"""
            
            response = self.gemini_client.generate_content(prompt)
            
            # Clean up the message
            message = self._clean_message(response.text)
            
            return message
            
        except Exception as e:
            print(f"AI message generation failed: {e}")
            return self._generate_fallback_message(candidate, job_description)
    
    def _generate_fallback_message(self, candidate: Dict, job_description: str) -> str:
        """
        Generate a fallback message when AI is not available
        """
        name = candidate.get('name', 'there')
        headline = candidate.get('headline', '')
        skills = candidate.get('skills', [])
        companies = candidate.get('companies', [])
        
        # Extract job title from job description
        job_title = self._extract_job_title(job_description)
        
        # Build fallback message
        message_parts = []
        
        # Greeting
        if name and name.lower() != 'unknown':
            message_parts.append(f"Hi {name},")
        else:
            message_parts.append("Hi there,")
        
        # Introduction
        if job_title:
            message_parts.append(f"I came across your profile and was impressed by your background in {job_title}.")
        else:
            message_parts.append("I came across your profile and was impressed by your professional background.")
        
        # Specific mention
        if companies:
            company_mention = f"Your experience at {companies[0]}"
            if skills:
                company_mention += f" and your skills in {', '.join(skills[:3])}"
            company_mention += " caught my attention."
            message_parts.append(company_mention)
        elif skills:
            message_parts.append(f"Your expertise in {', '.join(skills[:3])} is exactly what we're looking for.")
        
        # Job mention
        message_parts.append("We have an exciting opportunity that I think would be a great fit for your background.")
        
        # Call to action
        message_parts.append("Would you be interested in connecting to discuss this opportunity?")
        
        # Closing
        message_parts.append("Looking forward to hearing from you!")
        
        return " ".join(message_parts)
    
    def _extract_job_title(self, job_description: str) -> str:
        """
        Extract job title from job description
        """
        # Common job title patterns
        title_patterns = [
            r'(?:looking for|seeking|hiring)\s+(?:a\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:position|role|job)',
            r'(?:Senior|Junior|Lead|Principal)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback to common titles
        common_titles = ['Software Engineer', 'Developer', 'Data Scientist', 'Product Manager']
        job_lower = job_description.lower()
        
        for title in common_titles:
            if title.lower() in job_lower:
                return title
        
        return "this role"
    
    def _clean_message(self, message: str) -> str:
        """
        Clean and format the generated message
        """
        # Remove extra whitespace
        message = re.sub(r'\s+', ' ', message.strip())
        
        # Remove quotes if present
        message = re.sub(r'^["\']|["\']$', '', message)
        
        # Ensure proper sentence structure
        if not message.endswith(('.', '!', '?')):
            message += '.'
        
        # Limit length
        if len(message) > 500:
            sentences = message.split('.')
            shortened = []
            current_length = 0
            
            for sentence in sentences:
                if current_length + len(sentence) < 400:
                    shortened.append(sentence)
                    current_length += len(sentence)
                else:
                    break
            
            message = '. '.join(shortened) + '.'
        
        return message
    
    def get_message_quality_score(self, message: str) -> float:
        """
        Score the quality of a generated message (1-10)
        """
        score = 5.0  # Base score
        
        # Length check
        if 100 <= len(message) <= 300:
            score += 1.0
        elif len(message) < 50:
            score -= 2.0
        
        # Personalization check
        personal_indicators = ['your', 'you', 'specific', 'background', 'experience']
        personal_count = sum(1 for indicator in personal_indicators if indicator in message.lower())
        score += min(personal_count * 0.5, 2.0)
        
        # Call-to-action check
        cta_indicators = ['connect', 'discuss', 'schedule', 'call', 'meeting', 'opportunity']
        if any(cta in message.lower() for cta in cta_indicators):
            score += 1.0
        
        # Professional tone check
        unprofessional_words = ['hey', 'dude', 'awesome', 'cool', 'amazing']
        if any(word in message.lower() for word in unprofessional_words):
            score -= 1.0
        
        return min(max(score, 1.0), 10.0)
    
    def validate_message(self, message: str) -> bool:
        """
        Validate that message meets basic requirements
        """
        if not message or len(message.strip()) < 20:
            return False
        
        if len(message) > 500:
            return False
        
        # Check for basic structure
        if not any(word in message.lower() for word in ['hi', 'hello', 'connect', 'discuss']):
            return False
        
        return True
    
    def get_message_summary(self, message: str) -> str:
        """
        Generate a summary of the message
        """
        if len(message) <= 100:
            return message
        
        # Get first sentence and last sentence
        sentences = message.split('.')
        if len(sentences) >= 2:
            first = sentences[0].strip()
            last = sentences[-2].strip() if len(sentences) > 2 else sentences[-1].strip()
            return f"{first}. ... {last}."
        
        return message[:100] + "..." 