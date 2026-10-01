# Ultron — AI Voice & Web Assistant

A personal assistant with two interfaces: a **voice-controlled desktop CLI** (`ultron.py`) and a **web dashboard** (`app.py`, Flask) styled after Marvel's Ultron. It handles everyday commands — time, weather, jokes, quotes, Wikipedia lookups, opening apps/websites, basic math — and falls back to **Google Gemini** for open-ended questions, answered in character.

# 🌐 Live Demo

https://ultron-ai-chatbot.onrender.com/

> The Render deployment hosts the Flask web version. Browser voice features use the Web Speech API where supported.

## Features

- **Two run modes**
  - `ultron.py` — voice-only, listens via microphone (`SpeechRecognition`) and replies with speech (`pyttsx3`)
  - `app.py` — Flask web app with a themed dashboard UI (`templates/index.html`), text-based command input, and a REST API
- **Built-in commands**: greetings, time/date, weather (via wttr.in), system info (CPU/RAM/disk via `psutil`), jokes, motivational quotes, Wikipedia summaries, opening common sites (Google, YouTube, GitHub, Gmail, Calendar, Maps, etc.), opening system apps (Calculator, Notepad), basic arithmetic
- **AI fallback**: any command that doesn't match a built-in rule is sent to Gemini (`gemini-2.5-flash`) with a persona prompt so responses stay in character
- **Logging**: all commands and responses are logged to `logs/application.log`

## Tech Stack 

- **Backend**: Python, Flask, Flask-CORS
- **AI**: Google Gemini API (`google-genai`)
- **Browser voice**: Web Speech API
- **Desktop voice**: `SpeechRecognition`, `pyttsx3`, `pyaudio`
- **System monitoring**: `psutil`
- **Frontend**: HTML/CSS/JS (dashboard UI in `templates/index.html`)

## Project Structure

```
Ultron/
├── app.py                 # Flask web app + REST API
├── ultron.py               # Standalone voice-assistant CLI
├── requirements.txt
├── templates/
│   └── index.html          # Web dashboard UI
├── logs/                   # Runtime logs (not tracked in git)
└── .env                    # API keys (not tracked in git)
```

## Setup

1. **Clone and enter the project**
   ```bash
   git clone https://github.com/UjwalBagalkoti/Ultron-AI-Chatbot.git
   cd Ultron-AI-Chatbot
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   # source venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   ```

   > The cloud `requirements.txt` intentionally excludes desktop audio packages such as PyAudio. Install `SpeechRecognition`, `pyttsx3`, and `pyaudio` separately if you want to run `ultron.py` locally.

3. **Set up your API key**
   Set the Gemini API key in your environment:
   ```text
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   Get a key from [Google AI Studio](https://aistudio.google.com/).

4. **Run the web app**
   ```bash
   python app.py
   ```
   Visit `http://localhost:5000`.

   **Or run the voice CLI** (Windows only, due to `sapi5` TTS and `calc.exe`/`notepad.exe` calls):
   ```bash
   python ultron.py
   ```

## 🚀 Render Deployment

The web app can be deployed with:

```bash
pip install -r requirements.txt
gunicorn app:app
```

Set `GEMINI_API_KEY` as a Render environment variable. The desktop voice CLI should not be deployed to Render because it depends on local microphone/audio and OS capabilities.

## Notes

- `ultron.py` is Windows-specific (uses `sapi5` for text-to-speech and Windows executable paths for opening apps). `app.py` is cross-platform aside from optional OS-specific app-opening logic.
- The `/api/command` endpoint accepts `{"query": "..."}` and returns `{"response": "...", "action": "..."}` — useful if you want to build a different frontend against the same backend.
- Live news headlines aren't implemented; hook up a NewsAPI key in `get_news_headlines()` in `app.py` if you want that feature working.

## License

MIT — feel free to fork and extend.
