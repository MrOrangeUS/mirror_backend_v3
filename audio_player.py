# mirror_backend/audio_player.py

import os
import platform
import subprocess
import threading
from pathlib import Path
from queue import Queue
from typing import Optional

class AudioPlayer:
    def __init__(self):
        self.current_process: Optional[subprocess.Popen] = None
        self.audio_queue: Queue = Queue()
        self.is_playing = False
        self._player_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._player_thread.start()

    def _get_player_command(self, audio_path: str) -> list:
        """Get the appropriate player command for the current platform."""
        system = platform.system()
        path = str(Path(audio_path).resolve())
        
        if system == "Windows":
            return ["powershell", "-c", f"(New-Object Media.SoundPlayer '{path}').PlaySync()"]
        elif system == "Darwin":  # macOS
            return ["afplay", path]
        else:  # Linux
            return ["mpg123", "-q", path]

    def _play_audio_file(self, audio_path: str) -> bool:
        """Play a single audio file and return success status."""
        if not os.path.exists(audio_path):
            print(f"Audio file not found: {audio_path}")
            return False

        try:
            cmd = self._get_player_command(audio_path)
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.current_process.wait()
            return self.current_process.returncode == 0
        except Exception as e:
            print(f"Error playing audio: {str(e)}")
            return False
        finally:
            self.current_process = None

    def _process_queue(self):
        """Process the audio queue in a separate thread."""
        while True:
            audio_path = self.audio_queue.get()
            self.is_playing = True
            self._play_audio_file(audio_path)
            self.is_playing = False
            self.audio_queue.task_done()

    def play_audio(self, audio_path: str):
        """Add audio to the playback queue."""
        self.audio_queue.put(audio_path)

    def stop_current(self):
        """Stop the currently playing audio."""
        if self.current_process:
            self.current_process.terminate()
            self.current_process = None

    def clear_queue(self):
        """Clear the audio queue."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.task_done()
            except:
                pass

# Create singleton instance
audio_player = AudioPlayer()
