import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class APIMetrics:
    total_calls: int = 0
    total_errors: int = 0
    average_latency: float = 0.0
    last_error_time: Optional[float] = None
    last_error_message: Optional[str] = None

@dataclass
class ChatMetrics:
    total_comments: int = 0
    total_responses: int = 0
    unique_users: set = None
    response_rate: float = 0.0
    
    def __post_init__(self):
        if self.unique_users is None:
            self.unique_users = set()

@dataclass
class AudioMetrics:
    total_generations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_playback_time: float = 0.0
    failed_playbacks: int = 0

class MetricsCollector:
    def __init__(self, save_interval: int = 300):  # 5 minutes
        self.save_interval = save_interval
        self.last_save_time = time.time()
        self.start_time = time.time()
        self.metrics_dir = Path("metrics")
        self.metrics_dir.mkdir(exist_ok=True)
        
        # Initialize metrics
        self.gpt_metrics = APIMetrics()
        self.tts_metrics = APIMetrics()
        self.chat_metrics = ChatMetrics()
        self.audio_metrics = AudioMetrics()
        
        # Load previous metrics if available
        self._load_metrics()

    def get_uptime(self) -> str:
        """Get formatted uptime string."""
        uptime_seconds = int(time.time() - self.start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        return f"{hours}h {minutes}m"

    def _get_metrics_file(self) -> Path:
        """Get the metrics file path for the current day."""
        return self.metrics_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.json"

    def _save_metrics(self) -> None:
        """Save metrics to a JSON file."""
        try:
            metrics_data = {
                'timestamp': datetime.now().isoformat(),
                'uptime': self.get_uptime(),
                'gpt': asdict(self.gpt_metrics),
                'tts': asdict(self.tts_metrics),
                'chat': {
                    **asdict(self.chat_metrics),
                    'unique_users': list(self.chat_metrics.unique_users)
                },
                'audio': asdict(self.audio_metrics)
            }
            
            metrics_file = self._get_metrics_file()
            metrics_file.write_text(json.dumps(metrics_data, indent=2))
            logger.debug("Metrics saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving metrics: {str(e)}")

    def _load_metrics(self) -> None:
        """Load metrics from the last 24 hours."""
        try:
            yesterday = datetime.now() - timedelta(days=1)
            for day in [yesterday, datetime.now()]:
                metrics_file = self.metrics_dir / f"metrics_{day.strftime('%Y%m%d')}.json"
                if metrics_file.exists():
                    data = json.loads(metrics_file.read_text())
                    # Merge metrics...
                    logger.debug(f"Loaded metrics from {metrics_file.name}")
        except Exception as e:
            logger.error(f"Error loading metrics: {str(e)}")

    def record_api_call(self, api_type: str, latency: float, error: Optional[str] = None) -> None:
        """Record an API call metrics."""
        metrics = self.gpt_metrics if api_type == 'gpt' else self.tts_metrics
        
        metrics.total_calls += 1
        metrics.average_latency = (
            (metrics.average_latency * (metrics.total_calls - 1) + latency)
            / metrics.total_calls
        )
        
        if error:
            metrics.total_errors += 1
            metrics.last_error_time = time.time()
            metrics.last_error_message = error

        self._check_save()

    def record_chat_activity(self, username: str, response_sent: bool) -> None:
        """Record chat activity metrics."""
        self.chat_metrics.total_comments += 1
        self.chat_metrics.unique_users.add(username)
        
        if response_sent:
            self.chat_metrics.total_responses += 1
        
        self.chat_metrics.response_rate = (
            self.chat_metrics.total_responses / self.chat_metrics.total_comments
        )
        
        self._check_save()

    def record_audio_activity(self, duration: float, cached: bool, failed: bool = False) -> None:
        """Record audio activity metrics."""
        self.audio_metrics.total_generations += 1
        
        if cached:
            self.audio_metrics.cache_hits += 1
        else:
            self.audio_metrics.cache_misses += 1
            
        if failed:
            self.audio_metrics.failed_playbacks += 1
        else:
            self.audio_metrics.total_playback_time += duration
            
        self._check_save()

    def _check_save(self) -> None:
        """Check if metrics should be saved based on the interval."""
        current_time = time.time()
        if current_time - self.last_save_time >= self.save_interval:
            self._save_metrics()
            self.last_save_time = current_time

    def get_summary(self) -> Dict:
        """Get a summary of current metrics."""
        return {
            'uptime': self.get_uptime(),
            'gpt_success_rate': (
                (self.gpt_metrics.total_calls - self.gpt_metrics.total_errors)
                / max(1, self.gpt_metrics.total_calls)
            ) * 100,
            'tts_success_rate': (
                (self.tts_metrics.total_calls - self.tts_metrics.total_errors)
                / max(1, self.tts_metrics.total_calls)
            ) * 100,
            'chat_response_rate': self.chat_metrics.response_rate * 100,
            'unique_users': len(self.chat_metrics.unique_users),
            'cache_hit_rate': (
                self.audio_metrics.cache_hits
                / max(1, self.audio_metrics.total_generations)
            ) * 100,
            'average_gpt_latency': self.gpt_metrics.average_latency,
            'average_tts_latency': self.tts_metrics.average_latency
        }

# Create singleton instance
metrics_collector = MetricsCollector() 