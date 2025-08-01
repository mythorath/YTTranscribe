# 🎬 YT2TranscriptBot

A powerful command-line tool for extracting audio from YouTube videos and transcribing them to text with subtitle support. Supports both OpenAI Whisper API and local transcription with multiple output formats.

## ✨ Features

- 🎵 **Audio Extraction**: Downloads high-quality audio from YouTube using `yt-dlp`
- 🎤 **Dual Transcription**: OpenAI Whisper API or local `faster-whisper`
- 📄 **Multiple Formats**: Outputs `.txt`, `.srt`, and `.vtt` files
- 🧠 **AI Summarization**: Optional GPT-powered summaries
- 🛡️ **Robust Error Handling**: Graceful fallbacks and user-friendly messages
- 🔧 **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+**
2. **FFmpeg** (required for audio processing)
   ```bash
   # Windows (using Chocolatey)
   choco install ffmpeg
   
   # macOS (using Homebrew)
   brew install ffmpeg
   
   # Linux (Ubuntu/Debian)
   sudo apt install ffmpeg
   ```

3. **OpenAI API Key** (optional, for API transcription and summaries)
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Copy `.env.example` to `.env` and add your key:
     ```bash
     copy .env.example .env
     ```
   - Edit `.env` file:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd yt2transcriptbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key (optional)**
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Edit .env file and add your OpenAI API key
   # OPENAI_API_KEY=your_actual_api_key_here
   ```

### Basic Usage

```bash
# Basic transcription (local model)
python yt2transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Use OpenAI API
python yt2transcript.py "https://youtu.be/dQw4w9WgXcQ" --backend api

# With summary
python yt2transcript.py "https://youtu.be/dQw4w9WgXcQ" --summarize

# Custom model size and output directory
python yt2transcript.py "https://youtu.be/dQw4w9WgXcQ" --model-size small --output-dir ./my_transcripts
```

## 📋 Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `url` | YouTube URL to transcribe | **(required)** |
| `--output-dir` | Output directory for files | `./outputs` |
| `--backend` | Transcription method: `api`, `local`, `auto` | `local` |
| `--model-size` | Local model size: `tiny`, `base`, `small`, `medium`, `large` | `base` |
| `--api-key` | OpenAI API key | `$OPENAI_API_KEY` |
| `--summarize` | Create GPT summary | `false` |
| `--gpt-model` | GPT model: `gpt-3.5-turbo`, `gpt-4` | `gpt-3.5-turbo` |

## 📁 Output Structure

For each video, the tool creates a folder with the following files:

```
outputs/
└── Safe_Video_Title/
    ├── transcript.txt          # Raw transcript text
    ├── transcript.srt          # SubRip subtitle format
    ├── transcript.vtt          # WebVTT subtitle format
    └── summary.txt            # GPT summary (if --summarize used)
```

## 🔧 Architecture

```
┌─────────────────┐
│   YouTube URL   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Audio Extractor │  ← yt-dlp
│    (.mp3)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Transcriber    │  ← OpenAI API / faster-whisper
│ (text + timing) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ File Formatter  │  ← .txt, .srt, .vtt generation
│  + GPT Summary  │
└─────────────────┘
```

## 📦 Core Components

### 🎵 AudioExtractor (`src/audio_extractor.py`)
- URL validation and video info extraction
- High-quality audio download via `yt-dlp`
- Safe filename generation
- Temporary file management

### 🎤 Transcriber (`src/transcriber.py`)
- OpenAI Whisper API integration with file size handling
- Local `faster-whisper` with CPU optimization
- Automatic fallback between backends
- Word-level timestamp extraction

### 📄 FileFormatter (`src/file_formatter.py`)
- Multi-format output generation (TXT, SRT, VTT)
- Timestamp formatting for subtitles
- GPT-powered summarization
- Organized file structure management

## ⚡ Performance Comparison

| Backend | Speed | Cost | Accuracy | Output Formats |
|---------|-------|------|----------|----------------|
| **OpenAI API** | Fast | ~$0.006/min | Excellent | TXT only* |
| **Local (faster-whisper)** | Medium | Free | Excellent | TXT, SRT, VTT |

*API mode provides basic SRT/VTT with limited timing data

## 🛠️ Dependencies

### Python Packages
- `yt-dlp`: YouTube audio extraction
- `openai`: OpenAI API client
- `faster-whisper`: Local transcription engine
- `pydub`: Audio file manipulation
- `tqdm`: Progress bars

### System Requirements
- **FFmpeg**: Audio/video processing (critical dependency)
- **CUDA** (optional): GPU acceleration for local transcription

## 🐛 Troubleshooting

### Common Issues

**"FFmpeg not found"**
```bash
# Verify FFmpeg installation
ffmpeg -version

# Install if missing (Windows)
choco install ffmpeg
```

**"API rate limit exceeded"**
- Wait a few minutes and retry
- Consider using `--backend local` instead

**"File too large for API"**
- API has 25MB limit
- Automatically falls back to local processing

**"API key not found"**
```bash
# Test if your API key is loaded correctly
python test_api_key.py

# Make sure .env file exists and is formatted correctly
copy .env.example .env
# Then edit .env with your actual key
```

**"Local model loading fails"**
```bash
# Update faster-whisper
pip install -U faster-whisper

# Try smaller model
python yt2transcript.py URL --model-size tiny
```

### Debug Mode
Set environment variable for detailed logging:
```bash
export PYTHONASYNCIODEBUG=1
python yt2transcript.py URL --backend local
```

## 🔮 Future Enhancements

The following features are planned for future releases:

- 📺 **Playlist Support**: Process entire YouTube playlists
- 📊 **Batch Processing**: Handle multiple URLs from file
- 🎯 **Keyword Highlighting**: Highlight important terms in transcripts
- 👥 **Speaker Diarization**: Identify different speakers
- 🌍 **Multi-language**: Support for non-English transcription
- 🖥️ **GUI Interface**: Drag-and-drop web interface with Gradio
- 🧪 **Testing Suite**: Comprehensive unit and integration tests

## 📄 License

This project is released under the MIT License. See `LICENSE` file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for the Whisper model and API
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for robust YouTube downloading
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) for optimized local transcription

---

**Made with ❤️ for content creators, researchers, and accessibility advocates**
