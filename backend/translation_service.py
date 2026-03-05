"""
Translation Service using deep-translator
Provides multi-language support for the application

Author: Saurav Beri (@sauravberi16)
Role: Backend Developer - Multilingual Translation APIs
"""
import logging
from typing import Dict, Optional, List
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import deep-translator
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    logger.warning("deep-translator not installed. Translation features will be limited.")
    TRANSLATOR_AVAILABLE = False


# Language codes mapping
SUPPORTED_LANGUAGES = {
    "english": "en",
    "hindi": "hi",
    "punjabi": "pa",
    "marathi": "mr",
    "gujarati": "gu",
    "tamil": "ta",
    "telugu": "te",
    "bengali": "bn",
    "kannada": "kn",
    "malayalam": "ml",
    "odia": "or"
}

# Common UI text pre-translations for faster response
PRE_TRANSLATED = {
    "hi": {
        "Dashboard": "डैशबोर्ड",
        "Crop Recommendation": "फसल सिफारिश",
        "Weather": "मौसम",
        "Market Prices": "बाजार भाव",
        "Pest Detection": "कीट पहचान",
        "Disease Detection": "रोग पहचान",
        "Fertilizer Calculator": "उर्वरक कैलकुलेटर",
        "Pesticide Calculator": "कीटनाशक कैलकुलेटर",
        "Government Schemes": "सरकारी योजनाएं",
        "Expert Contact": "विशेषज्ञ संपर्क",
        "Community": "समुदाय",
        "Profile": "प्रोफ़ाइल",
        "Settings": "सेटिंग्स",
        "Logout": "लॉग आउट",
        "Login": "लॉग इन",
        "Register": "पंजीकरण",
        "Welcome": "स्वागत है",
        "Search": "खोजें",
        "Submit": "जमा करें",
        "Cancel": "रद्द करें",
        "Save": "सहेजें",
        "Loading": "लोड हो रहा है",
        "Error": "त्रुटि",
        "Success": "सफलता",
        "Temperature": "तापमान",
        "Humidity": "आर्द्रता",
        "Rainfall": "वर्षा",
        "Soil Type": "मिट्टी का प्रकार",
        "Nitrogen": "नाइट्रोजन",
        "Phosphorus": "फास्फोरस",
        "Potassium": "पोटेशियम",
        "pH Level": "पीएच स्तर",
        "Water Source": "जल स्रोत",
        "Upload Image": "छवि अपलोड करें",
        "Detect": "पता लगाएं",
        "Results": "परिणाम",
        "Recommendations": "सिफारिशें",
        "Treatment": "उपचार",
        "Prevention": "रोकथाम",
        "Healthy": "स्वस्थ",
        "Diseased": "रोगग्रस्त",
    },
    "pa": {
        "Dashboard": "ਡੈਸ਼ਬੋਰਡ",
        "Crop Recommendation": "ਫਸਲ ਸਿਫਾਰਿਸ਼",
        "Weather": "ਮੌਸਮ",
        "Market Prices": "ਬਾਜ਼ਾਰ ਭਾਅ",
        "Pest Detection": "ਕੀੜੇ ਦੀ ਪਛਾਣ",
        "Disease Detection": "ਬਿਮਾਰੀ ਦੀ ਪਛਾਣ",
        "Fertilizer Calculator": "ਖਾਦ ਕੈਲਕੁਲੇਟਰ",
        "Government Schemes": "ਸਰਕਾਰੀ ਯੋਜਨਾਵਾਂ",
        "Welcome": "ਜੀ ਆਇਆਂ ਨੂੰ",
        "Search": "ਖੋਜੋ",
        "Submit": "ਜਮ੍ਹਾਂ ਕਰੋ",
        "Temperature": "ਤਾਪਮਾਨ",
        "Humidity": "ਨਮੀ",
        "Healthy": "ਸਿਹਤਮੰਦ",
    },
    "mr": {
        "Dashboard": "डॅशबोर्ड",
        "Crop Recommendation": "पीक शिफारस",
        "Weather": "हवामान",
        "Market Prices": "बाजारभाव",
        "Pest Detection": "कीड ओळख",
        "Disease Detection": "रोग ओळख",
        "Fertilizer Calculator": "खत कॅल्क्युलेटर",
        "Government Schemes": "सरकारी योजना",
        "Welcome": "स्वागत आहे",
        "Search": "शोधा",
        "Submit": "सबमिट करा",
        "Temperature": "तापमान",
        "Humidity": "आर्द्रता",
        "Healthy": "निरोगी",
    },
    "gu": {
        "Dashboard": "ડેશબોર્ડ",
        "Crop Recommendation": "પાક ભલામણ",
        "Weather": "હવામાન",
        "Market Prices": "બજાર ભાવ",
        "Pest Detection": "જીવાત શોધ",
        "Disease Detection": "રોગ શોધ",
        "Fertilizer Calculator": "ખાતર કેલ્ક્યુલેટર",
        "Government Schemes": "સરકારી યોજનાઓ",
        "Welcome": "સ્વાગત છે",
        "Search": "શોધો",
        "Submit": "સબમિટ કરો",
        "Temperature": "તાપમાન",
        "Humidity": "ભેજ",
        "Healthy": "સ્વસ્થ",
    },
    "ta": {
        "Dashboard": "டாஷ்போர்டு",
        "Crop Recommendation": "பயிர் பரிந்துரை",
        "Weather": "வானிலை",
        "Market Prices": "சந்தை விலை",
        "Pest Detection": "பூச்சி கண்டறிதல்",
        "Disease Detection": "நோய் கண்டறிதல்",
        "Fertilizer Calculator": "உரம் கணிப்பான்",
        "Government Schemes": "அரசு திட்டங்கள்",
        "Welcome": "வரவேற்கிறோம்",
        "Search": "தேடு",
        "Submit": "சமர்ப்பி",
        "Temperature": "வெப்பநிலை",
        "Humidity": "ஈரப்பதம்",
        "Healthy": "ஆரோக்கியமான",
    },
    "te": {
        "Dashboard": "డాష్‌బోర్డ్",
        "Crop Recommendation": "పంట సిఫార్సు",
        "Weather": "వాతావరణం",
        "Market Prices": "మార్కెట్ ధరలు",
        "Pest Detection": "పురుగుల గుర్తింపు",
        "Disease Detection": "వ్యాధి గుర్తింపు",
        "Fertilizer Calculator": "ఎరువుల కాల్క్యులేటర్",
        "Government Schemes": "ప్రభుత్వ పథకాలు",
        "Welcome": "స్వాగతం",
        "Search": "వెతకండి",
        "Submit": "సమర్పించండి",
        "Temperature": "ఉష్ణోగ్రత",
        "Humidity": "తేమ",
        "Healthy": "ఆరోగ్యకరమైన",
    }
}


class TranslationService:
    """Service for translating text to multiple Indian languages"""
    
    def __init__(self):
        self.available = TRANSLATOR_AVAILABLE
        self._cache = {}
    
    def get_language_code(self, language: str) -> str:
        """Get language code from language name or code"""
        lang_lower = language.lower()
        
        # If it's already a code, check if it's valid
        if lang_lower in SUPPORTED_LANGUAGES.values():
            return lang_lower
        
        # Otherwise, look up by name
        return SUPPORTED_LANGUAGES.get(lang_lower, "en")
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages"""
        return [
            {"code": code, "name": name.title()}
            for name, code in SUPPORTED_LANGUAGES.items()
        ]
    
    def translate(
        self,
        text: str,
        target_language: str,
        source_language: str = "en"
    ) -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language (name or code)
            source_language: Source language (default: English)
            
        Returns:
            Translated text
        """
        # Get language code
        target_code = self.get_language_code(target_language)
        if target_code == "en":
            return text  # No translation needed
        
        # Check pre-translated cache
        if target_code in PRE_TRANSLATED:
            if text in PRE_TRANSLATED[target_code]:
                return PRE_TRANSLATED[target_code][text]
        
        # Check runtime cache
        cache_key = f"{source_language}:{target_code}:{text}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Use Google Translator
        if not self.available:
            return text  # Return original if translator not available
        
        try:
            translator = GoogleTranslator(source=source_language, target=target_code)
            translated = translator.translate(text)
            
            # Cache the result
            self._cache[cache_key] = translated
            return translated
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    def translate_batch(
        self,
        texts: List[str],
        target_language: str,
        source_language: str = "en"
    ) -> List[str]:
        """Translate multiple texts"""
        return [
            self.translate(text, target_language, source_language)
            for text in texts
        ]
    
    def translate_dict(
        self,
        data: Dict[str, str],
        target_language: str,
        source_language: str = "en"
    ) -> Dict[str, str]:
        """Translate all string values in a dictionary"""
        return {
            key: self.translate(value, target_language, source_language)
            if isinstance(value, str) else value
            for key, value in data.items()
        }
    
    def get_ui_translations(self, language: str) -> Dict[str, str]:
        """Get all UI translations for a language"""
        lang_code = self.get_language_code(language)
        
        if lang_code == "en":
            # Return English keys as-is
            return {key: key for key in PRE_TRANSLATED.get("hi", {}).keys()}
        
        if lang_code in PRE_TRANSLATED:
            return PRE_TRANSLATED[lang_code]
        
        # Translate on-the-fly if not pre-translated
        if self.available:
            try:
                english_texts = list(PRE_TRANSLATED.get("hi", {}).keys())
                translations = {}
                
                for text in english_texts:
                    translations[text] = self.translate(text, lang_code)
                
                return translations
            except Exception as e:
                logger.error(f"Error generating translations: {e}")
        
        return {}


# Singleton instance
_service = None

def get_translation_service() -> TranslationService:
    """Get or create translation service"""
    global _service
    if _service is None:
        _service = TranslationService()
    return _service


# Test if run directly
if __name__ == "__main__":
    service = get_translation_service()
    
    print(f"Translator available: {service.available}")
    print(f"Supported languages: {service.get_supported_languages()}")
    
    # Test translation
    test_texts = ["Dashboard", "Crop Recommendation", "Weather", "Market Prices"]
    
    for lang in ["hindi", "punjabi", "tamil"]:
        print(f"\n{lang.title()}:")
        for text in test_texts:
            translated = service.translate(text, lang)
            print(f"  {text} -> {translated}")
