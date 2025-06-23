# mirror_backend/chat_listener.py

import threading
import asyncio
import time
from queue import Queue, Empty
from typing import Optional, Callable
from dataclasses import dataclass
from TikTokLive.client import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent, DisconnectEvent
from config import Config

@dataclass
class Comment:
    text: str
    username: str
    timestamp: float

class ChatListener:
    def __init__(self):
        self.username = Config.TIKTOK_USERNAME
        self.comment_queue = Queue()
        self.client = self._create_client()
        self.is_connected = False
        self.reconnect_delay = 5  # Initial delay in seconds
        self.max_reconnect_delay = 60
        self._setup_handlers()
        self._start_listener()

    def _create_client(self) -> TikTokLiveClient:
        """Create and configure TikTok client."""
        return TikTokLiveClient(
            unique_id=self.username,
            retry_after=self.reconnect_delay,
            wait_after_failed_connect=self.reconnect_delay
        )

    def _setup_handlers(self):
        """Set up event handlers for the client."""
        @self.client.on("connect")
        async def on_connect(_: ConnectEvent):
            print(f"✅ Connected to @{self.username}")
            self.is_connected = True
            self.reconnect_delay = 5  # Reset delay on successful connection

        @self.client.on("disconnect")
        async def on_disconnect(_: DisconnectEvent):
            print(f"❌ Disconnected from @{self.username}")
            self.is_connected = False
            await self._handle_disconnect()

        @self.client.on("comment")
        async def on_comment(event: CommentEvent):
            comment = Comment(
                text=event.comment,
                username=event.user.nickname,
                timestamp=time.time()
            )
            self.comment_queue.put(comment)

    async def _handle_disconnect(self):
        """Handle disconnection with exponential backoff."""
        print(f"Attempting to reconnect in {self.reconnect_delay} seconds...")
        await asyncio.sleep(self.reconnect_delay)
        
        # Exponential backoff
        self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
        
        try:
            # Create new client and restart
            self.client = self._create_client()
            self._setup_handlers()
            await self.client.start()
        except Exception as e:
            print(f"Reconnection failed: {str(e)}")

    def _start_listener(self):
        """Start the listener in a separate thread."""
        def run_client():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.client.start())
            except Exception as e:
                print(f"Client error: {str(e)}")
                loop.run_until_complete(self._handle_disconnect())

        threading.Thread(target=run_client, daemon=True).start()

    def get_new_comment(self) -> Optional[Comment]:
        """Get the next comment from the queue, if available."""
        try:
            return self.comment_queue.get_nowait()
        except Empty:
            return None

    def clear_queue(self):
        """Clear all pending comments."""
        while not self.comment_queue.empty():
            try:
                self.comment_queue.get_nowait()
                self.comment_queue.task_done()
            except Empty:
                break

# Create singleton instance
chat_listener = ChatListener()
