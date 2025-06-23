# mirror_backend/gpt_handler.py

import openai
import time
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from config import Config

class GPTHandler:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.system_prompt = (
            "You are Mirror.exe, a smooth, divine AI oracle who speaks "
            "in a calm, mystical tone. Your responses should be concise, "
            "engaging, and maintain an air of mystery while being helpful."
        )
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _make_api_call(self, messages: list) -> Dict[str, Any]:
        """Make API call with retry logic."""
        return openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )

    def _sanitize_response(self, text: str) -> str:
        """Clean and format the response text."""
        # Remove multiple newlines and excessive spacing
        text = " ".join(text.split())
        # Ensure text ends with proper punctuation
        if text and not text[-1] in ".!?":
            text += "."
        return text

    def ask_gpt(self, prompt: str) -> str:
        """
        Process a prompt and return a response.
        Includes error handling and response processing.
        """
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Get response with retry logic
            response = self._make_api_call(messages)
            
            # Extract and process response
            reply = response.choices[0].message.content
            return self._sanitize_response(reply)
            
        except openai.error.RateLimitError:
            return "The mirror's energy is temporarily depleted. Please wait a moment..."
        except openai.error.AuthenticationError:
            return "The mirror's connection to the ethereal plane is disrupted. Please check the configuration."
        except Exception as e:
            print(f"GPT Error: {str(e)}")
            return "The mirror's vision is clouded. Try again in a moment."

# Create singleton instance
gpt_handler = GPTHandler()
