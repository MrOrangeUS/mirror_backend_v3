# Mirror.exe - AI Oracle TikTok Live Bot

A mystical AI oracle that responds to TikTok live chat comments with ethereal wisdom, powered by GPT-4 and ElevenLabs text-to-speech.

## Features

- 🎭 Mystical AI persona that engages with viewers
- 🗣️ Natural text-to-speech responses using ElevenLabs
- 💾 Audio caching system for improved performance
- 📊 Comprehensive metrics tracking
- 🔄 Automatic reconnection handling
- 📝 Detailed logging system

## Prerequisites

- Python 3.8 or higher
- TikTok account for live streaming
- OpenAI API key
- ElevenLabs API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mirror_exe.git
cd mirror_exe
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
VOICE_ID=your_voice_id_here
TIKTOK_USERNAME=your_tiktok_username
```

## Usage

1. Start the bot:
```bash
python mirror_main.py
```

2. The bot will:
- Connect to your TikTok live stream
- Listen for chat messages
- Generate mystical responses using GPT-4
- Convert responses to speech using ElevenLabs
- Play audio responses
- Send periodic engagement prompts

## Configuration

The bot can be configured through the following files:

- `config.py`: Main configuration settings
- `logging_config.py`: Logging settings
- `.env`: API keys and sensitive data

## Project Structure

```
mirror_exe/
├── mirror_main.py      # Main application
├── chat_listener.py    # TikTok chat interface
├── gpt_handler.py      # GPT-4 integration
├── tts_handler.py      # Text-to-speech handling
├── audio_player.py     # Audio playback
├── cache_manager.py    # Audio cache management
├── metrics.py          # Performance tracking
├── config.py           # Configuration
├── logging_config.py   # Logging setup
├── requirements.txt    # Dependencies
└── README.md          # Documentation
```

## Metrics and Monitoring

The bot collects various metrics:
- API success rates and latencies
- Chat engagement statistics
- Audio cache performance
- Unique user tracking

Metrics are saved to JSON files in the `metrics/` directory.

## Logging

Logs are stored in the `logs/` directory with:
- Colored console output
- Daily rotating log files
- Different log levels for debugging

## Cache Management

Audio responses are cached to improve performance:
- Configurable cache size limit
- Automatic cleanup of old files
- Cache hit/miss tracking

## Error Handling

The bot includes comprehensive error handling:
- Automatic reconnection for disconnects
- API error recovery
- Graceful shutdown handling

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 