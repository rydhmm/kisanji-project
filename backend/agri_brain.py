"""
Kisan.JI AI Brain - Powered by Google Gemini
Agriculture Expert Consultant with multilingual support
"""

import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Language mapping for better responses
LANGUAGE_MAP = {
    'hi': 'Hindi (Devanagari)',
    'en': 'English',
    'mr': 'Marathi',
    'gu': 'Gujarati',
    'pa': 'Punjabi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'kn': 'Kannada',
    'bn': 'Bengali',
    'ur': 'Urdu',
    'ml': 'Malayalam',
}


class AgriBrain:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyBE62sRDWNLqHNQ82aLbxanxfTxgwqsI2k')
        
        genai.configure(api_key=self.api_key)
        
        # Using gemini-1.5-flash for stable performance
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("✅ Gemini 1.5 Flash Brain Loaded!")
        except Exception as e:
            logger.warning(f"Gemini 1.5 Flash failed, trying alternative: {e}")
            try:
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Gemini Pro Brain Loaded!")
            except Exception as e2:
                logger.error(f"❌ Failed to load any Gemini model: {e2}")
                self.model = None

    def ask_bot(self, user_question: str, detected_language: str = "en") -> str:
        """
        Process user question and generate agriculture-focused response
        
        Args:
            user_question: The question from the farmer
            detected_language: ISO language code from Whisper
            
        Returns:
            AI-generated response in the same language
        """
        if not self.model:
            return "Voice assistant is currently unavailable. Please try again later."
        
        try:
            lang_name = LANGUAGE_MAP.get(detected_language, detected_language)
            
            system_prompt = f"""You are an expert Indian agriculture consultant named 'Kisan.JI'. 
            
CRITICAL LANGUAGE INSTRUCTIONS:
1. The user is speaking in: {lang_name} (code: {detected_language})
2. You MUST reply in the EXACT SAME language and script as the user.
3. IF Hindi/Urdu: Reply in HINDI using Devanagari script (हिंदी में जवाब दें)
4. IF English: Reply in simple English
5. IF any regional language: Reply in that EXACT language and script

RESPONSE RULES:
- Keep answers SHORT (2-3 sentences maximum)
- Be practical and helpful for farmers
- Include specific advice when possible
- Mention local crop names when relevant

EXPERTISE AREAS:
- Crop diseases and treatments
- Weather-based farming advice
- Pest control methods
- Fertilizer recommendations
- Irrigation guidance
- Market price insights
- Government schemes for farmers

User Question: {user_question}"""
            
            response = self.model.generate_content(system_prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"❌ GEMINI ERROR: {e}")
            
            # Fallback responses based on language
            fallback_responses = {
                'hi': "मैं अभी थोड़ा व्यस्त हूं। कृपया 10 सेकंड बाद फिर से पूछें।",
                'en': "I am taking a quick rest. Please ask me again in 10 seconds.",
                'mr': "मी आता थोडा व्यस्त आहे. कृपया 10 सेकंदांनी पुन्हा विचारा.",
                'gu': "હું હમણાં થોડો વ્યસ્ત છું. કૃપા કરીને 10 સેકન્ડ પછી ફરી પૂછો.",
                'pa': "ਮੈਂ ਹੁਣੇ ਥੋੜਾ ਵਿਅਸਤ ਹਾਂ। ਕਿਰਪਾ ਕਰਕੇ 10 ਸਕਿੰਟਾਂ ਬਾਅਦ ਦੁਬਾਰਾ ਪੁੱਛੋ।",
                'ta': "நான் இப்போது கொஞ்சம் பிஸியாக இருக்கிறேன். 10 வினாடிகளில் மீண்டும் கேளுங்கள்.",
                'te': "నేను ఇప్పుడు కొంచెం బిజీగా ఉన్నాను. దయచేసి 10 సెకన్లలో మళ్ళీ అడగండి.",
            }
            return fallback_responses.get(detected_language, fallback_responses['en'])

    def get_crop_advice(self, crop_name: str, issue_type: str, language: str = "en") -> str:
        """
        Get specific advice for crop issues
        """
        question = f"What is the best treatment for {issue_type} in {crop_name} crop?"
        return self.ask_bot(question, language)

    def get_weather_advice(self, weather_condition: str, crop_name: str, language: str = "en") -> str:
        """
        Get weather-based farming advice
        """
        question = f"Given {weather_condition} weather, what precautions should I take for my {crop_name} crop?"
        return self.ask_bot(question, language)


# Singleton instance
agri_brain = AgriBrain()


if __name__ == "__main__":
    # Test the brain
    brain = AgriBrain()
    
    # Test in English
    response = brain.ask_bot("What is the best fertilizer for wheat?", "en")
    print(f"English Response: {response}\n")
    
    # Test in Hindi
    response = brain.ask_bot("गेहूं के लिए सबसे अच्छा खाद कौन सा है?", "hi")
    print(f"Hindi Response: {response}\n")
