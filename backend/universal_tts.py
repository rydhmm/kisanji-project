"""
Universal TTS - Text-to-Speech with Voice Cloning
Uses XTTS v2 for multilingual speech synthesis

Author: Ankit Negi (@anku251)
Role: AI/ML Engineer - Voice Synthesis & TTS Integration
"""

import torch
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default reference audio directory
AUDIO_DIR = Path(__file__).parent / "audio_references"
AUDIO_DIR.mkdir(exist_ok=True)

# Language codes supported by XTTS v2
SUPPORTED_LANGUAGES = [
    'en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl',
    'cs', 'ar', 'zh-cn', 'ja', 'hu', 'ko', 'hi'
]

# Map Whisper language codes to TTS language codes
LANGUAGE_MAP = {
    'hi': 'hi',      # Hindi
    'en': 'en',      # English
    'mr': 'hi',      # Marathi -> Hindi (closest supported)
    'gu': 'hi',      # Gujarati -> Hindi
    'pa': 'hi',      # Punjabi -> Hindi
    'bn': 'hi',      # Bengali -> Hindi
    'ta': 'hi',      # Tamil -> Hindi (TTS limitation)
    'te': 'hi',      # Telugu -> Hindi
    'kn': 'hi',      # Kannada -> Hindi
    'ml': 'hi',      # Malayalam -> Hindi
    'ur': 'hi',      # Urdu -> Hindi
}


class UniversalTTS:
    def __init__(self, lazy_load=True):
        """
        Initialize Universal TTS
        
        Args:
            lazy_load: If True, model is loaded only when first needed
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = None
        self.is_loaded = False
        
        if not lazy_load:
            self._load_model()
    
    def _load_model(self):
        """Load the XTTS v2 model"""
        if self.is_loaded:
            return True
            
        try:
            from TTS.api import TTS
            
            logger.info(f"⏳ Loading Universal Voice Model on {self.device}...")
            logger.info("📥 First run will download ~2GB model. Please wait...")
            
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            self.is_loaded = True
            logger.info("✅ Universal TTS Model Loaded!")
            return True
            
        except ImportError:
            logger.error("❌ TTS library not installed. Run: pip install TTS")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load TTS model: {e}")
            return False

    def generate_audio(
        self, 
        text: str, 
        reference_audio_path: str = None,
        language: str = "en", 
        output_path: str = "output_response.wav"
    ) -> str:
        """
        Generate speech audio from text
        
        Args:
            text: Text to convert to speech
            reference_audio_path: Path to voice sample for cloning (5-10 seconds recommended)
            language: Language code (en, hi, etc.)
            output_path: Where to save the generated audio
            
        Returns:
            Path to generated audio file, or None on failure
        """
        # Lazy load model
        if not self.is_loaded:
            if not self._load_model():
                return None
        
        # Map language code
        tts_language = LANGUAGE_MAP.get(language, 'en')
        
        # Use default reference audio if not provided
        if reference_audio_path is None:
            reference_audio_path = AUDIO_DIR / "default_voice.wav"
            
            # Create a default voice sample if it doesn't exist
            if not reference_audio_path.exists():
                logger.warning("No reference audio found. Using model's default voice.")
                return self._generate_without_cloning(text, tts_language, output_path)
        
        # Validate reference audio
        if not os.path.exists(reference_audio_path):
            logger.warning(f"⚠️ Reference audio not found: {reference_audio_path}")
            return self._generate_without_cloning(text, tts_language, output_path)

        # Clean up old file
        if os.path.exists(output_path):
            os.remove(output_path)

        try:
            # Generate speech with voice cloning
            self.tts.tts_to_file(
                text=text,
                speaker_wav=str(reference_audio_path),
                language=tts_language,
                file_path=output_path
            )
            
            logger.info(f"✅ Audio generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ TTS generation failed: {e}")
            return None

    def _generate_without_cloning(self, text: str, language: str, output_path: str) -> str:
        """Generate audio without voice cloning (fallback)"""
        try:
            # Try using a simpler TTS model without cloning
            from TTS.api import TTS
            
            simple_tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(self.device)
            simple_tts.tts_to_file(text=text, file_path=output_path)
            
            logger.info(f"✅ Audio generated (no cloning): {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Simple TTS also failed: {e}")
            return None

    def list_available_voices(self) -> list:
        """List available TTS models"""
        try:
            from TTS.api import TTS
            return TTS().list_models()
        except:
            return []


# Singleton instance - lazy loaded
_tts_engine = None

def get_tts_engine():
    """Get or create the TTS engine singleton"""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = UniversalTTS(lazy_load=True)
    return _tts_engine


if __name__ == "__main__":
    logger.info("--- Universal TTS System Online ---")
    
    # Test initialization
    tts = UniversalTTS(lazy_load=False)
    
    # Test generation
    test_text = "Hello! I am Kisan.JI, your farming assistant."
    output = tts.generate_audio(test_text, language="en")
    
    if output:
        print(f"Generated audio at: {output}")
    else:
        print("TTS test failed")
