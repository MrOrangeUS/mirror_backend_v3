import os
import time
from pathlib import Path
from typing import Optional, List, Tuple
from config import config
from logging_config import get_logger

logger = get_logger(__name__)

class CacheManager:
    def __init__(self, cache_dir: Path = config.audio.cache_dir):
        self.cache_dir = cache_dir
        self.max_size_bytes = config.audio.max_cache_size_mb * 1024 * 1024
        self.cache_dir.mkdir(exist_ok=True)
        
    def get_cache_stats(self) -> Tuple[int, int]:
        """Return current cache size and file count."""
        total_size = 0
        file_count = 0
        
        for file in self.cache_dir.glob("*.mp3"):
            if file.is_file():
                total_size += file.stat().st_size
                file_count += 1
                
        return total_size, file_count

    def cleanup_cache(self) -> None:
        """Remove old files if cache exceeds maximum size."""
        total_size, _ = self.get_cache_stats()
        
        if total_size <= self.max_size_bytes:
            return

        # Get list of files with their timestamps
        files: List[Tuple[float, Path]] = []
        for file in self.cache_dir.glob("*.mp3"):
            if file.is_file():
                files.append((file.stat().st_mtime, file))

        # Sort by timestamp (oldest first)
        files.sort()

        # Remove files until we're under the limit
        for mtime, file in files:
            if total_size <= self.max_size_bytes:
                break
                
            try:
                size = file.stat().st_size
                file.unlink()
                total_size -= size
                logger.debug(f"Removed cached file: {file.name}")
            except Exception as e:
                logger.error(f"Error removing cache file {file}: {str(e)}")

    def get_cached_file(self, file_hash: str) -> Optional[Path]:
        """Get a cached file if it exists."""
        cache_path = self.cache_dir / f"{file_hash}.mp3"
        return cache_path if cache_path.is_file() else None

    def add_to_cache(self, file_hash: str, audio_data: bytes) -> Path:
        """Add a new file to the cache."""
        # Clean up if necessary
        self.cleanup_cache()
        
        # Save new file
        cache_path = self.cache_dir / f"{file_hash}.mp3"
        cache_path.write_bytes(audio_data)
        logger.debug(f"Added new file to cache: {cache_path.name}")
        
        return cache_path

    def clear_cache(self) -> None:
        """Clear all cached files."""
        try:
            for file in self.cache_dir.glob("*.mp3"):
                if file.is_file():
                    file.unlink()
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")

# Create singleton instance
cache_manager = CacheManager() 