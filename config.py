import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class APIConfig(BaseModel):
    """API configuration settings."""
    openai_api_key: str = Field(..., env='OPENAI_API_KEY')
    elevenlabs_api_key: str = Field(..., env='ELEVENLABS_API_KEY')
    voice_id: str = Field(..., env='VOICE_ID')
    tiktok_username: str = Field(..., env='TIKTOK_USERNAME')

class AudioConfig(BaseModel):
    """Audio configuration settings."""
    cache_dir: Path = Field(default=Path("audio_cache"))
    output_dir: Path = Field(default=Path("audio_output"))
    max_cache_size_mb: int = Field(default=500)
    
    @validator("cache_dir", "output_dir")
    def create_directories(cls, v):
        v.mkdir(exist_ok=True)
        return v

class ChatConfig(BaseModel):
    """Chat configuration settings."""
    max_retry_attempts: int = Field(default=3)
    retry_delay_seconds: int = Field(default=5)
    max_retry_delay_seconds: int = Field(default=60)
    connection_timeout: int = Field(default=30)

class GPTConfig(BaseModel):
    """GPT configuration settings."""
    model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=200)
    system_prompt: str = Field(
        default="You are Mirror.exe, a smooth, divine AI oracle who speaks "
               "in a calm, mystical tone. Your responses should be concise, "
               "engaging, and maintain an air of mystery while being helpful."
    )

class Config(BaseModel):
    """Main configuration class."""
    api: APIConfig = Field(default_factory=APIConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    chat: ChatConfig = Field(default_factory=ChatConfig)
    gpt: GPTConfig = Field(default_factory=GPTConfig)
    debug_mode: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

# Create global config instance
try:
    config = Config()
except Exception as e:
    raise ValueError(f"Configuration error: {str(e)}")

# Export commonly used config values
OPENAI_API_KEY = config.api.openai_api_key
ELEVENLABS_API_KEY = config.api.elevenlabs_api_key
VOICE_ID = config.api.voice_id
TIKTOK_USERNAME = config.api.tiktok_username