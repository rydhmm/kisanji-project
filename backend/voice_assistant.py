"""
Voice Assistant Service
Integrates Whisper (STT) + Gemini (AI) + XTTS (TTS)
Complete voice-to-voice agriculture assistant
"""

import os
import uuid
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directories for audio files
UPLOAD_DIR = Path(__file__).parent / "uploads"
OUTPUT_DIR = Path(__file__).parent / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


class VoiceAssistant:
    """
    Complete voice assistant that:
    1. Transcribes user speech (Whisper)
    2. Generates AI response (Gemini)
    3. Converts response to speech (XTTS)
    4. Stores queries in database
    """
    
    def __init__(self, db=None):
        """
        Initialize voice assistant
        
        Args:
            db: MongoDB database instance for storing voice queries
        """
        self.db = db
        self.voice_processor = None
        self.agri_brain = None
        self.tts_engine = None
        
        # Lazy load components
        self._init_components()
    
    def _init_components(self):
        """Initialize AI components (lazy loading)"""
        try:
            from agri_brain import agri_brain
            self.agri_brain = agri_brain
            logger.info("✅ AgriBrain loaded")
        except Exception as e:
            logger.warning(f"AgriBrain not loaded: {e}")
        
        # Voice processor and TTS are loaded on-demand to save memory
    
    def _get_voice_processor(self):
        """Get or create voice processor"""
        if self.voice_processor is None:
            try:
                from voice_processor import get_voice_engine
                self.voice_processor = get_voice_engine()
            except Exception as e:
                logger.error(f"Failed to load voice processor: {e}")
        return self.voice_processor
    
    def _get_tts_engine(self):
        """Get or create TTS engine"""
        if self.tts_engine is None:
            try:
                from universal_tts import get_tts_engine
                self.tts_engine = get_tts_engine()
            except Exception as e:
                logger.error(f"Failed to load TTS engine: {e}")
        return self.tts_engine
    
    async def process_voice_query(
        self, 
        audio_path: str,
        farmer_id: Optional[str] = None,
        generate_audio_response: bool = True,
        reference_voice: Optional[str] = None
    ) -> dict:
        """
        Process a complete voice query
        
        Args:
            audio_path: Path to user's audio file
            farmer_id: Optional farmer ID for database storage
            generate_audio_response: Whether to generate audio response
            reference_voice: Path to voice sample for TTS cloning
            
        Returns:
            dict: {
                'success': bool,
                'transcription': str,
                'language': str,
                'response': str,
                'audio_response': str (path to audio file),
                'query_id': str
            }
        """
        result = {
            'success': False,
            'transcription': '',
            'language': 'unknown',
            'response': '',
            'audio_response': None,
            'query_id': None
        }
        
        # Step 1: Transcribe audio
        logger.info("🎤 Step 1: Transcribing audio...")
        processor = self._get_voice_processor()
        
        if processor:
            transcription = processor.transcribe(audio_path)
            result['transcription'] = transcription.get('text', '')
            result['language'] = transcription.get('language', 'en')
            
            if not transcription.get('success', False):
                result['response'] = "Sorry, I couldn't understand the audio. Please try again."
                return result
        else:
            result['response'] = "Voice processing is not available."
            return result
        
        # Step 2: Get AI response
        logger.info("🧠 Step 2: Getting AI response...")
        if self.agri_brain and result['transcription']:
            result['response'] = self.agri_brain.ask_bot(
                result['transcription'],
                result['language']
            )
        else:
            result['response'] = "I'm having trouble thinking right now. Please try again."
        
        # Step 3: Generate audio response (optional)
        if generate_audio_response and result['response']:
            logger.info("🔊 Step 3: Generating audio response...")
            tts = self._get_tts_engine()
            
            if tts:
                output_filename = f"response_{uuid.uuid4().hex[:8]}.wav"
                output_path = OUTPUT_DIR / output_filename
                
                audio_file = tts.generate_audio(
                    text=result['response'],
                    reference_audio_path=reference_voice,
                    language=result['language'],
                    output_path=str(output_path)
                )
                
                if audio_file:
                    result['audio_response'] = audio_file
        
        # Step 4: Store in database
        if self.db and result['transcription']:
            logger.info("💾 Step 4: Storing query in database...")
            query_id = await self._store_query(
                farmer_id=farmer_id,
                transcription=result['transcription'],
                language=result['language'],
                response=result['response'],
                audio_response=result.get('audio_response')
            )
            result['query_id'] = query_id
        
        result['success'] = True
        logger.info("✅ Voice query processed successfully!")
        return result
    
    async def _store_query(
        self,
        farmer_id: str,
        transcription: str,
        language: str,
        response: str,
        audio_response: str
    ) -> str:
        """Store voice query in database"""
        try:
            query_doc = {
                "query_id": str(uuid.uuid4()),
                "farmer_id": farmer_id,
                "query_text": transcription,
                "language": language,
                "response": response,
                "audio_response_path": audio_response,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "completed"
            }
            
            await self.db.voice_queries.insert_one(query_doc)
            logger.info(f"Stored voice query: {query_doc['query_id']}")
            return query_doc['query_id']
            
        except Exception as e:
            logger.error(f"Failed to store query: {e}")
            return None
    
    def process_text_query(self, text: str, language: str = "en") -> str:
        """
        Process a text-only query (for chatbot fallback)
        
        Args:
            text: User's question
            language: Language code
            
        Returns:
            AI response text
        """
        if self.agri_brain:
            return self.agri_brain.ask_bot(text, language)
        return "I'm not available right now. Please try again later."


# Factory function to create voice assistant with database
def create_voice_assistant(db=None):
    """Create a VoiceAssistant instance with optional database"""
    return VoiceAssistant(db=db)


if __name__ == "__main__":
    # Test the voice assistant (text mode)
    assistant = VoiceAssistant()
    
    # Test text query
    response = assistant.process_text_query(
        "What is the best fertilizer for wheat?",
        "en"
    )
    print(f"Response: {response}")
