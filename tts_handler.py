# mirror_backend/tts_handler.py

import os
import hashlib
import requests
from pathlib import Path
from typing import Optional
from config import Config

class TTSHandler:
    def __init__(self):
        self.api_key = Config.ELEVENLABS_API_KEY
        self.voice_id = Config.VOICE_ID
        self.cache_dir = Path("audio_cache")
        self.output_dir = Path("audio_output")
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure necessary directories exist."""
        self.cache_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

    def _get_cache_path(self, text: str) -> Path:
        """Generate a cache path for the given text."""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return self.cache_dir / f"{text_hash}.mp3"

    def _make_api_request(self, text: str) -> Optional[bytes]:
        """Make API request to ElevenLabs."""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "speaking_rate": 1.0
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"TTS API Error: {str(e)}")
            return None

    def speak_text(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Convert text to speech, with caching and error handling.
        Returns the path to the audio file or None if generation failed.
        """
        try:
            # Check cache first
            cache_path = self._get_cache_path(text)
            if cache_path.exists():
                audio_data = cache_path.read_bytes()
            else:
                # Generate new audio
                audio_data = self._make_api_request(text)
                if audio_data is None:
                    return None
                # Save to cache
                cache_path.write_bytes(audio_data)

            # Determine output path
            final_path = Path(output_path) if output_path else self.output_dir / "output.mp3"
            
            # Save to output location
            final_path.write_bytes(audio_data)
            return str(final_path)

        except Exception as e:
            print(f"TTS Error: {str(e)}")
            return None

# Create singleton instance
tts_handler = TTSHandler()
