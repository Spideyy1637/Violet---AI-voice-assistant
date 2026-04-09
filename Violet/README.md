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
- 🏠 **IoT Integration** - Control smart home devices (lights, fans) with voice via ESP32
- 📡 **ESP32 Support** - Real hardware relay control over Wi-Fi

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
├── iot/                 # IoT hardware code
│   └── violet_iot/
│       └── violet_iot.ino   # ESP32 Arduino sketch
└── violet-web/          # React frontend (Vite)
    ├── src/
    │   ├── components/
    │   │   └── ui/
    │   │       └── IoTPanel.tsx  # IoT dashboard panel
    │   └── ...
    ├── package.json
    └── index.html
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
| `turn on the light` | Turn ON the light (IoT) |
| `turn off the light` | Turn OFF the light (IoT) |
| `turn on the fan` | Turn ON the fan (IoT) |
| `turn off the fan` | Turn OFF the fan (IoT) |
| `device status` | Check IoT device states |
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
cd violet-web && npm install && npm run dev
```

---

## 🏠 IoT Connection (ESP32 Smart Home Control)

VIOLET can control real physical devices like lights and fans using an **ESP32** microcontroller and a **relay module** over Wi-Fi.

### Hardware Requirements

| Component | Purpose |
|---|---|
| **ESP32 Dev Board** | Wi-Fi-enabled microcontroller |
| **2-Channel Relay Module (5V)** | Switches devices ON/OFF |
| **Breadboard** | Prototyping connections |
| **Jumper Wires** (M-M, M-F) | Connect components |
| **USB Cable** (Micro-USB) | Power + program ESP32 |
| **12V DC Adapter** | Power supply |
| **Power Supply Module** | Regulated power to breadboard |
| **LED / Bulb / DC Fan** | Devices to control |

### Wiring Diagram

```
ESP32              Relay Module
──────             ────────────
GPIO 26  ────────→  IN1 (Light)
GPIO 27  ────────→  IN2 (Fan)
GND      ────────→  GND
5V / VIN ────────→  VCC
```

### Software Setup

**Step 1:** Install [Arduino IDE](https://www.arduino.cc/en/software)

**Step 2:** Add ESP32 board support:
- Go to **File → Preferences**
- Add this URL to "Additional Board Manager URLs":
  ```
  https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
  ```
- Go to **Tools → Board → Board Manager** → Search **"ESP32"** → Install

**Step 3:** Install required Arduino library:
- Go to **Sketch → Include Library → Manage Libraries**
- Search **"ArduinoJson"** by Benoit Blanchon → Install

**Step 4:** Open `iot/violet_iot/violet_iot.ino` in Arduino IDE

**Step 5:** Update Wi-Fi credentials in the sketch:
```cpp
const char* WIFI_SSID     = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD  = "YOUR_WIFI_PASSWORD";
```

**Step 6:** Select board & upload:
- **Tools → Board → ESP32 Dev Module**
- **Tools → Port → (your COM port)**
- Click **Upload** ✅

**Step 7:** Open **Serial Monitor** (115200 baud) and note the **IP address** displayed

**Step 8:** Update `server.py` with the ESP32's IP:
```python
ESP32_IP = "192.168.1.105"  # ← Replace with your ESP32's IP
```

### How It Works

```
User: "Turn on the light"
         │
         ▼
┌─────────────────────┐
│  VIOLET Backend     │  Parses command → Sends HTTP request
│  (server.py)        │  GET http://ESP32_IP/relay1/on
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  ESP32 (Wi-Fi)      │  Sets GPIO 26 HIGH → Relay clicks
│  violet_iot.ino     │
└─────────────────────┘
         │
         ▼
      💡 Light ON!
```

### IoT Voice Commands

| Voice Command | Action |
|---|---|
| "Turn on the light" | Activates Relay 1 (GPIO 26) |
| "Turn off the light" | Deactivates Relay 1 |
| "Turn on the fan" | Activates Relay 2 (GPIO 27) |
| "Turn off the fan" | Deactivates Relay 2 |
| "Switch on/off the lamp" | Controls light (alias) |
| "Device status" | Shows all device states |
| "Smart home status" | Shows all device states |

### IoT REST API

| Endpoint | Method | Description |
|---|---|---|
| `/api/iot/status` | GET | Returns device states + ESP32 connection |
| `/api/iot/control` | POST | Control devices. Body: `{"device": "light", "action": "on"}` |

### IoT Dashboard (Web UI)

Click the 🏠 **Home** icon button in the VIOLET header bar to open the IoT Dashboard panel:
- Toggle switches for Light and Fan
- Real-time connection status indicator
- Auto-refreshes every 5 seconds

### ESP32 Direct Access

You can also control devices directly from a browser by visiting:
- `http://<ESP32_IP>/` — Control dashboard
- `http://<ESP32_IP>/status` — JSON status
- `http://<ESP32_IP>/relay1/on` — Light ON
- `http://<ESP32_IP>/relay1/off` — Light OFF
- `http://<ESP32_IP>/relay2/on` — Fan ON
- `http://<ESP32_IP>/relay2/off` — Fan OFF

---

## 📝 License

This project is for personal use.

---

## 🙋 Support

If you encounter any issues:
1. Check the Troubleshooting section above
2. Make sure all dependencies are installed
3. Verify your internet connection for Gemini AI
4. For IoT issues, check that ESP32 is on the same Wi-Fi network

---

Made with 💜 by VIOLET Assistant
