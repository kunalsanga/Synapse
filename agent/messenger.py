"""
Enhanced Message Generator for Synapse Hackathon
Creates personalized outreach messages highlighting candidate characteristics
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
        Generate personalized outreach messages for candidates
        """
        candidates_with_messages = []
        
        for candidate in candidates:
            try:
                message = self._generate_single_message(candidate, job_description)
                candidate['outreach_message'] = message
                candidates_with_messages.append(candidate)
            except Exception as e:
                print(f"Error generating message for {candidate.get('name', 'Unknown')}: {e}")
                # Fallback message
                candidate['outreach_message'] = self._generate_fallback_message(candidate, job_description)
                candidates_with_messages.append(candidate)
        
        return candidates_with_messages
    
    def _generate_single_message(self, candidate: Dict, job_description: str) -> str:
        """
        Generate a personalized message for a single candidate
        """
        if self.gemini_client:
            return self._generate_ai_message(candidate, job_description)
        else:
            return self._generate_rule_based_message(candidate, job_description)
    
    def _generate_ai_message(self, candidate: Dict, job_description: str) -> str:
        """
        Generate AI-powered personalized message
        """
        try:
            # Extract candidate details
            name = candidate.get('name', 'there')
            headline = candidate.get('headline', '')
            location = candidate.get('location', '')
            skills = candidate.get('skills', [])
            companies = candidate.get('companies', [])
            education = candidate.get('education', [])
            fit_score = candidate.get('fit_score', 0)
            score_breakdown = candidate.get('score_breakdown', {})
            
            # Create personalized prompt
            prompt = self._create_personalization_prompt(
                name, headline, location, skills, companies, education, 
                fit_score, score_breakdown, job_description
            )
            
            response = self.gemini_client.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"AI message generation failed: {e}")
            return self._generate_rule_based_message(candidate, job_description)
    
    def _create_personalization_prompt(self, name: str, headline: str, location: str, 
                                     skills: List[str], companies: List[str], 
                                     education: List[str], fit_score: float,
                                     score_breakdown: Dict, job_description: str) -> str:
        """
        Create a detailed prompt for personalized message generation
        """
        # Extract top strengths from score breakdown
        strengths = []
        for category, score in score_breakdown.items():
            if score >= 8.0:
                strengths.append(f"{category} ({score}/10)")
        
        # Format candidate details
        skills_text = ', '.join(skills[:5]) if skills else 'technical skills'
        companies_text = ', '.join(companies[:3]) if companies else 'previous companies'
        education_text = ', '.join(education[:2]) if education else 'educational background'
        
        prompt = f"""
You are a professional recruiter reaching out to a potential candidate. Create a personalized LinkedIn outreach message that:

1. Uses the candidate's first name naturally
2. References specific details from their profile
3. Explains why they're a great fit for the role
4. Maintains a professional yet friendly tone
5. Is concise (150-200 words max)

Candidate Details:
- Name: {name}
- Current Role: {headline}
- Location: {location}
- Key Skills: {skills_text}
- Previous Companies: {companies_text}
- Education: {education_text}
- Overall Fit Score: {fit_score}/10
- Top Strengths: {', '.join(strengths) if strengths else 'Strong technical background'}

Job Description:
{job_description}

Create a compelling, personalized message that highlights their specific qualifications and how they align with this opportunity. Be specific about what makes them stand out.
"""
        return prompt
    
    def _generate_rule_based_message(self, candidate: Dict, job_description: str) -> str:
        """
        Generate rule-based personalized message
        """
        name = candidate.get('name', 'there')
        headline = candidate.get('headline', '')
        location = candidate.get('location', '')
        skills = candidate.get('skills', [])
        companies = candidate.get('companies', [])
        education = candidate.get('education', [])
        fit_score = candidate.get('fit_score', 0)
        score_breakdown = candidate.get('score_breakdown', {})
        
        # Extract key information for personalization
        top_skills = skills[:3] if skills else []
        top_companies = companies[:2] if companies else []
        top_education = education[:1] if education else []
        
        # Find top strengths
        strengths = []
        for category, score in score_breakdown.items():
            if score >= 8.0:
                if category == 'education' and top_education:
                    strengths.append(f"strong {category} from {top_education[0]}")
                elif category == 'company' and top_companies:
                    strengths.append(f"impressive {category} experience at {top_companies[0]}")
                elif category == 'skills' and top_skills:
                    strengths.append(f"excellent {category} including {', '.join(top_skills)}")
                else:
                    strengths.append(f"strong {category}")
        
        # Build personalized message
        message_parts = []
        
        # Opening
        if name and name != 'there':
            message_parts.append(f"Hi {name.split()[0]},")
        else:
            message_parts.append("Hi there,")
        
        # Personalization based on strengths
        if strengths:
            strength_text = ', '.join(strengths)
            message_parts.append(f"I came across your profile and was impressed by your {strength_text}.")
        else:
            message_parts.append("I came across your profile and was impressed by your background.")
        
        # Company experience mention
        if top_companies:
            message_parts.append(f"Your experience at {top_companies[0]} particularly caught my attention.")
        
        # Skills mention
        if top_skills:
            skills_text = ', '.join(top_skills)
            message_parts.append(f"Your expertise in {skills_text} aligns perfectly with what we're looking for.")
        
        # Job fit mention
        if fit_score >= 8.0:
            message_parts.append("Based on your background, you'd be an excellent fit for this role.")
        elif fit_score >= 6.0:
            message_parts.append("Your background shows strong potential for this opportunity.")
        else:
            message_parts.append("I believe your experience could be valuable for this position.")
        
        # Call to action
        message_parts.append("Would you be interested in learning more about this opportunity? I'd love to discuss how your skills could contribute to our team.")
        
        # Closing
        message_parts.append("Looking forward to connecting!")
        
        return ' '.join(message_parts)
    
    def _generate_fallback_message(self, candidate: Dict, job_description: str) -> str:
        """
        Generate a simple fallback message
        """
        name = candidate.get('name', 'there')
        headline = candidate.get('headline', '')
        
        if name and name != 'there':
            first_name = name.split()[0]
            message = f"Hi {first_name}, I noticed your profile and your experience as {headline}. "
        else:
            message = "Hi there, I noticed your profile and your professional experience. "
        
        message += "I believe you could be a great fit for an exciting opportunity we have. "
        message += "Would you be interested in learning more? Looking forward to connecting!"
        
        return message
    
    def generate_batch_messages(self, candidates: List[Dict], job_description: str) -> List[Dict]:
        """
        Generate messages for multiple candidates efficiently
        """
        return self.generate_outreach_messages(candidates, job_description)
    
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