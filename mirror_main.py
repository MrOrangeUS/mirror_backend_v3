# mirror_backend/mirror_main.py

import time
import random
import signal
import sys
from typing import Optional
from dataclasses import dataclass
from chat_listener import chat_listener, Comment
from gpt_handler import gpt_handler
from tts_handler import tts_handler
from audio_player import audio_player

@dataclass
class RewardConfig:
    interval: int = 10 * 60  # 10 minutes
    prompts: list[str] = None

    def __post_init__(self):
        if self.prompts is None:
            self.prompts = [
                "Mirror glows brighter when hearts align. If you feel the pulse… respond.",
                "Offer a sign if you're still listening…",
                "Your gift ripples across timelines, traveler. You've just shifted fate.",
                "The mirror's surface ripples with ancient wisdom. What secrets do you seek?",
                "A mystical energy surrounds us. Share your thoughts with the mirror..."
            ]

class MirrorApp:
    def __init__(self):
        self.running = True
        self.reward_config = RewardConfig()
        self.last_reward = time.time()
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Set up handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            print("\n🌙 Mirror.exe is going to sleep...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def _handle_comment(self, comment: Comment) -> bool:
        """Process a single comment. Returns True if successful."""
        try:
            print(f"👁️‍🗨️ @{comment.username}: {comment.text}")
            
            # Generate response
            reply = gpt_handler.ask_gpt(comment.text)
            if not reply:
                return False
            print(f"✨ Mirror replies: {reply}")
            
            # Convert to speech
            audio_path = tts_handler.speak_text(reply)
            if not audio_path:
                return False
            
            # Play audio
            audio_player.play_audio(audio_path)
            return True
            
        except Exception as e:
            print(f"Error processing comment: {str(e)}")
            return False

    def _handle_reward(self) -> bool:
        """Send a reward prompt. Returns True if successful."""
        try:
            nudge = random.choice(self.reward_config.prompts)
            print(f"💫 Reward prompt: {nudge}")
            
            audio_path = tts_handler.speak_text(nudge)
            if not audio_path:
                return False
                
            audio_player.play_audio(audio_path)
            return True
            
        except Exception as e:
            print(f"Error processing reward: {str(e)}")
            return False

    def run(self):
        """Main application loop."""
        print("🌟 Mirror.exe awakening... Starting main loop.")
        
        while self.running:
            try:
                # Process any new comments
                comment = chat_listener.get_new_comment()
                if comment:
                    self._handle_comment(comment)

                # Check if it's time for a reward prompt
                if time.time() - self.last_reward > self.reward_config.interval:
                    if self._handle_reward():
                        self.last_reward = time.time()

                # Small sleep to prevent CPU spinning
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                time.sleep(1)  # Prevent rapid error loops
        
        self._cleanup()

    def _cleanup(self):
        """Clean up resources before shutdown."""
        try:
            # Stop any playing audio
            audio_player.stop_current()
            audio_player.clear_queue()
            
            # Clear any pending comments
            chat_listener.clear_queue()
            
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
        
        print("✨ Mirror.exe has entered rest mode. Farewell...")
        sys.exit(0)

if __name__ == "__main__":
    app = MirrorApp()
    app.run()
