# VIOLET - Voice Interactive Lightweight Engine for Tasks

VIOLET is an advanced AI-powered voice assistant designed for seamless interaction and smart home control. Built with a modern tech stack, it features a stunning React-based 3D interface, real-time voice recognition, and IoT integration.

---

## 🌟 Key Features

-   **Voice-First Interface**: Real-time speech-to-text and text-to-speech interaction.
-   **AI Integration**: Powered by Google Gemini AI for intelligent conversations and task processing.
-   **3D Visuals**: Immersive login and chat experience using Spline and Three.js (Aurora Borealis shaders).
-   **Smart Home Control**: Integration with ESP32/IoT devices to control lights, fans, and more.
-   **Multi-Utility**: News updates, weather forecasts, math calculations, reminders, and web search.
-   **Local Knowledge**: Includes an offline dataset for quick responses to common queries.

---

## 🛠️ Tech Stack

-   **Frontend**: React, Vite, Tailwind CSS, Three.js, Framer Motion, Spline.
-   **Backend**: Python, FastAPI, Uvicorn.
-   **AI**: Google Gemini Pro (Generative AI).
-   **IoT**: Arduino/C++ (for ESP32).

---

## 🚀 Getting Started

### 1. Prerequisites

-   **Python 3.10+**
-   **Node.js 18+**
-   **Git** (optional)

### 2. Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Spideyy1637/Violet---AI-voice-assistant.git
    cd Violet
    ```

2.  **Install Backend Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Frontend Dependencies**:
    ```bash
    npm install
    npm run install:all
    ```

### 3. Configuration

1.  Create a `.env` file in the root directory (based on `.env.example`):
    ```env
    GEMINI_API_KEY=your_gemini_api_key
    GNEWS_API_KEY=your_gnews_api_key
    ```
    -   Get a Gemini API Key from [Google AI Studio](https://aistudio.google.com/).
    -   Get a GNews API Key from [GNews.io](https://gnews.io/).

2.  **IoT Setup (Optional)**:
    -   Open `iot/violet_iot/violet_iot.ino` in Arduino IDE.
    -   Update your Wi-Fi credentials and ESP32 IP in `server.py` (line 45).

---

## 💻 Running the Application

You can run both the backend and frontend simultaneously using the root development script:

```bash
npm run dev
```

Alternatively, run them separately:

-   **Backend**: `python server.py` (runs on port 8001)
-   **Frontend**: `cd violet-web && npm run dev` (runs on port 5173)

---

## 🎤 Usage

1.  **Login**: Use voice commands like "Violet" or "Login" at the 3D login screen to enter.
2.  **Interact**: Speak naturally to ask questions, check weather, or control your IoT devices.
3.  **Commands**:
    -   "What's the weather in London?"
    -   "Turn on the lights."
    -   "Tell me the latest news from India."
    -   "Calculate the square root of 144."
    -   "Search for the best hiking trails nearby."

---

## 📁 Project Structure

-   `server.py`: Main FastAPI backend server handling AI, logic, and IoT.
-   `violet-web/`: React frontend application.
-   `iot/`: Arduino source code for ESP32 hardware integration.
-   `config.py`: Configuration and environment variable loader.
-   `dataset.json`: Offline knowledge base for quick responses.

---

## 📄 License

This project is open-source. Please credit the original authors when sharing or modifying.
