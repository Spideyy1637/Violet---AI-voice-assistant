# 🟣 VIOLET - Voice Interactive Lightweight Engine for Tasks

A personal AI voice assistant powered by Google Gemini AI with both voice and text input capabilities. VIOLET can help you with various tasks like checking time/date, weather, opening applications, web searches, and answering questions.

---

## ✨ Features

- 🎤 **Voice Input** - Speak naturally and get responses
- ⌨️ **Text Input** - Type messages when voice isn't convenient
- 🤖 **Gemini AI** - Powered by Google's Gemini AI for intelligent responses
- 🗣️ **Text-to-Speech** - VIOLET speaks back to you with a female voice
- 🌐 **Web UI** - Beautiful React-based web interface
- ⚡ **Quick Commands** - Time, date, weather, app launching, and web search

---

## 📁 Project Structure

```
Violet/
├── main.py              # Main CLI voice assistant (standalone)
├── server.py            # FastAPI backend server for web UI
├── config.py            # Configuration file
├── requirements.txt     # Python dependencies
├── assistant.py         # Assistant helper functions
├── handlers.py          # Command handlers
├── utils.py             # Utility functions
└── violet-web/          # React frontend (Vite)
    ├── src/             # React source code
    ├── package.json     # Node.js dependencies
    └── index.html       # Entry HTML file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/) (for web UI only)
- **Microphone** - Required for voice input

---

## 📥 Installation

### Step 1: Clone or Download the Project

Download the project folder to your computer.

### Step 2: Install Python Dependencies

Open a terminal/command prompt in the `Violet` folder and run:

```bash
# Windows
pip install -r requirements.txt

# Additional packages for Voice, Server, and AI
pip install sounddevice numpy google-genai fastapi uvicorn cryptography python-dotenv
```

### Step 3: Generate SSL Certificates (Required)

VIOLET runs securely on HTTPS. Generate local certificates before starting:

```bash
python generate_cert.py
```

### Step 4: Install Web UI Dependencies (Optional)

If you want to use the web interface:

```bash
cd violet-web
npm install
```

---

## 🎮 Running the Application

### Option 1: Command Line Mode (Standalone)

Run the CLI voice assistant directly:

```bash
python main.py
```

**Controls:**
- Speak or type commands
- Type `voice` to switch to voice mode
- Type `text` to switch to text mode
- Type `exit`, `quit`, or `bye` to stop

---

### Option 2: Web Interface Mode

**Step 1:** Start the backend server:

```bash
python server.py
```

The server will start at `https://0.0.0.0:8000` (HTTPS)

**Step 2:** In a new terminal, start the web UI:

```bash
cd violet-web
npm run dev
```

The web UI will open at `https://localhost:5173`

---

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `time` or `what time is it` | Get current time |
| `date` or `what day is it` | Get current date |
| `weather` | Get weather information |
| `open chrome` | Open Google Chrome |
| `open notepad` | Open Notepad |
| `open calculator` | Open Calculator |
| `open firefox` | Open Firefox |
| `open edge` | Open Microsoft Edge |
| `search <query>` | Search Google for something |
| `hello` / `hi` | Greet VIOLET |
| Any other question | Ask Gemini AI |

---

## ⚙️ Configuration

### API Key

The project uses Google Gemini API. The API key is configured in:
- `main.py` (line 216)
- `server.py` (line 16)
- `config.py` (GEMINI_API_KEY)

To use your own API key:
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Replace the existing key in the files above

### Environment Variables (Optional)

Create a `.env` file in the `Violet` folder:

```env
GEMINI_API_KEY=your_api_key_here
```

---

## 🛠️ Troubleshooting

### Common Issues

**1. "No module named 'sounddevice'"**
```bash
pip install sounddevice numpy
```

**2. "No module named 'google.genai'"**
```bash
pip install google-genai
```

**3. "No module named 'pyttsx3'"**
```bash
pip install pyttsx3
```

**4. PyAudio installation fails on Windows**
```bash
pip install pipwin
pipwin install pyaudio
```

**5. Microphone not detected**
- Check if your microphone is connected
- Ensure microphone permissions are enabled
- Try running as administrator

**6. Voice input not working**
- VIOLET will automatically switch to text mode
- Type your messages instead

---

## 💻 System Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Windows 10/11, macOS, Linux |
| Python | 3.8 or higher |
| Node.js | 18 or higher (for web UI) |
| RAM | 4GB minimum |
| Microphone | Required for voice input |
| Internet | Required for Gemini AI |

---

## 📦 Dependencies

### Python Packages

| Package | Purpose |
|---------|---------|
| `pyttsx3` | Text-to-speech |
| `requests` | HTTP requests for weather |
| `sounddevice` | Microphone audio recording |
| `numpy` | Audio processing |
| `python-dotenv` | Environment variables |
| `google-genai` | Google Gemini AI |
| `fastapi` | Web API server |
| `uvicorn` | ASGI server |

### Node.js Packages (Web UI)

| Package | Purpose |
|---------|---------|
| `react` | UI framework |
| `vite` | Build tool |

---

## 🎯 Quick Start Commands

```bash
# Install all dependencies at once
pip install pyttsx3 requests sounddevice numpy python-dotenv google-genai fastapi uvicorn cryptography

# Generate Certificates
python generate_cert.py

# Run CLI mode
python main.py

# Run web mode (2 terminals needed)
# Terminal 1:
python server.py
# Terminal 2:
cd violet-web && npm install && 

























































```

---

## 📝 License

This project is for personal use.

---

## 🙋 Support

If you encounter any issues:
1. Check the Troubleshooting section above
2. Make sure all dependencies are installed
3. Verify your internet connection for Gemini AI

---

Made with 💜 by VIOLET Assistant
