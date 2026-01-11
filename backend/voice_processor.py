"""
Voice Processor - Whisper-based Speech Recognition
Supports multilingual transcription with automatic language detection
"""

import whisper
import os
import logging
import warnings
from pathlib import Path

# Suppress FP16 warnings on CPU (Clean logs)
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Language code to name mapping
LANGUAGE_NAMES = {
    'hi': 'Hindi',
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
    'or': 'Odia',
    'as': 'Assamese',
}


class VoiceProcessor:
    def __init__(self, model_size="base"):
        """
        Initialize Whisper model for speech recognition
        
        Args:
            model_size: 'tiny', 'base', 'small', 'medium', 'large'
                       - tiny: Fastest, less accurate
                       - base: Good balance (recommended for most cases)
                       - small: Better accuracy, slower
                       - medium/large: Best accuracy, requires more RAM
        """
        self.model_size = model_size
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the Whisper model"""
        try:
            logger.info(f"⏳ Initializing Whisper '{self.model_size}' model...")
            self.model = whisper.load_model(self.model_size)
            logger.info(f"✅ Voice model loaded. Ready for multilingual input.")
        except Exception as e:
            logger.critical(f"❌ Voice model failed to load: {e}")
            self.model = None

    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribe audio file and auto-detect language.
        
        Args:
            audio_path: Path to audio file (WAV, MP3, FLAC, etc.)
            
        Returns:
            dict: {
                'text': transcribed text,
                'language': detected language code,
                'language_name': human-readable language name,
                'success': bool
            }
        """
        if not self.model:
            logger.error("Voice model not loaded")
            return {
                "text": "",
                "language": "unknown",
                "language_name": "Unknown",
                "success": False
            }

        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return {
                "text": "",
                "language": "unknown",
                "language_name": "Unknown",
                "success": False
            }

        try:
            logger.info(f"🎤 Processing audio: {audio_path}")
            
            # fp16=False is crucial for CPU inference
            result = self.model.transcribe(audio_path, fp16=False)
            
            detected_lang = result.get('language', 'en')
            lang_name = LANGUAGE_NAMES.get(detected_lang, detected_lang.title())
            
            logger.info(f"✅ Transcription complete | Language: {lang_name}")
            logger.info(f"📝 Text: {result['text'][:100]}...")
            
            return {
                "text": result["text"].strip(),
                "language": detected_lang,
                "language_name": lang_name,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            return {
                "text": "",
                "language": "unknown",
                "language_name": "Unknown",
                "success": False
            }

    def transcribe_with_timestamps(self, audio_path: str) -> dict:
        """
        Transcribe audio with word-level timestamps
        Useful for subtitle generation
        """
        if not self.model or not os.path.exists(audio_path):
            return {"segments": [], "success": False}
            
        try:
            result = self.model.transcribe(
                audio_path, 
                fp16=False,
                word_timestamps=True
            )
            
            return {
                "text": result["text"],
                "language": result.get('language', 'en'),
                "segments": result.get("segments", []),
                "success": True
            }
        except Exception as e:
            logger.error(f"Transcription with timestamps failed: {e}")
            return {"segments": [], "success": False}


# Singleton Instance - lazy loaded
_voice_engine = None

def get_voice_engine():
    """Get or create the voice engine singleton"""
    global _voice_engine
    if _voice_engine is None:
        _voice_engine = VoiceProcessor(model_size="base")
    return _voice_engine


if __name__ == "__main__":
    logger.info("--- Voice Processing System Online ---")
    
    # Test initialization
    processor = VoiceProcessor()
    
    # Test with a sample audio file (if exists)
    test_audio = "test_audio.wav"
    if os.path.exists(test_audio):
        result = processor.transcribe(test_audio)
        print(f"Transcription Result: {result}")
    else:
        print("No test audio file found. System is ready for audio input.")
