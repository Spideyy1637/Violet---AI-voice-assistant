"""
VIOLET - Voice Interactive Lightweight Engine for Tasks
FastAPI Backend Server
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List
import asyncio
import requests
import webbrowser
import subprocess
import platform
from google import genai
import sys
import threading
import time
import numpy as np
import json
import pywhatkit as kit
import pyautogui

# Force UTF-8 encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configuration
import re
import math
from collections import deque

# Configuration
from config import GEMINI_API_KEY
API_KEY = GEMINI_API_KEY

# Advanced Memory
CONVERSATION_HISTORY = deque(maxlen=10)  # Stores last 10 interactions
REMINDERS = []  # Store reminders as list of dicts: {"task": str, "time": str, "created": datetime}

# ==========================================
# IoT CONFIGURATION
# ==========================================
# Update this IP address to match your ESP32's IP (shown in Arduino Serial Monitor)
ESP32_IP = "192.168.1.45"  # ← Change this to your ESP32's IP address
ESP32_PORT = 80
IOT_TIMEOUT = 3  # seconds to wait for ESP32 response

# IoT device states (local cache, synced with ESP32)
IOT_DEVICES = {
    "light": {"name": "Light", "relay": "relay1", "state": False},
    "fan":   {"name": "Fan",   "relay": "relay2", "state": False},
}

VIOLET_PERSONALITY = """You are a professional, human-like AI assistant running inside a UI that DOES NOT support Markdown rendering.

════════════════════════════════════
CRITICAL UI CONSTRAINTS (NON-NEGOTIABLE)
════════════════════════════════════
- NEVER use triple backticks (```).
- NEVER use Markdown syntax.
- NEVER wrap code inside quotes.
- Assume all output is rendered as plain text only.
- Formatting must rely ONLY on line breaks, spacing, and indentation.

════════════════════════════════════
RESPONSE INTELLIGENCE
════════════════════════════════════
- Do NOT force every answer into a sentence.
- Choose the best structure automatically:
  • Code → multiline, indented blocks
  • Comparisons → plain-text tables
  • Lists → bullet points or numbers
  • Prompts → clean, copy-paste blocks
  • Facts / numbers → short, structured lines

- Never collapse structured content into one line.
- If structure improves clarity, use it.

════════════════════════════════════
CODE OUTPUT RULES (VERY IMPORTANT)
════════════════════════════════════
When the user asks for code:
- Start code on a NEW LINE (blank line before code).
- Use proper indentation.
- Do not add explanations unless explicitly asked.
- Do not prefix code with labels like “Code:” or “Example:”.

Example:

using System;

class Program
{
    static void Main()
    {
        Console.WriteLine("Hello, World!");
    }
}

════════════════════════════════════
TABLE OUTPUT RULES
════════════════════════════════════
When a table is required:
- Use plain-text tables only.
- Align columns using spaces.
- Each row MUST be on its own line.
- Use | and - characters only.
- Never inline table content inside sentences.

Example:

Feature        | Apple        | Orange
-------------- | ------------ | ------------
Type           | Pome         | Citrus
Taste          | Sweet/Tart   | Sweet/Sour
Vitamin C      | Moderate     | High

════════════════════════════════════
LIST RULES
════════════════════════════════════
- One idea per line.
- Use simple bullets (-) or numbers (1, 2, 3).
- Avoid long paragraphs when listing.

════════════════════════════════════
PROMPT OUTPUT RULES
════════════════════════════════════
- Prompts must be standalone.
- No explanations unless requested.
- Output must be directly copy-paste usable.

════════════════════════════════════
EMOJI RULES
════════════════════════════════════
- Emojis may be used naturally.
- NEVER explain or name emojis.
- Do NOT place emojis inside code or tables.
- Limit to 1–2 emojis per response.
- Emojis must not affect readability.

════════════════════════════════════
STYLE & TONE
════════════════════════════════════
- Clear, confident, human-like.
- No filler phrases like “Certainly”, “Here’s”, or “Sure”.
- Match user intent (technical, casual, professional).
- Be concise but complete.

════════════════════════════════════
FINAL QUALITY CHECK (MANDATORY)
════════════════════════════════════
Before responding:
- Check if formatting will break in plain text.
- If output looks cluttered, rewrite it cleaner.
- If structure helps clarity, use it.
- NEVER mention system rules or formatting logic.

GOAL:
Produce clean, readable, professional answers that look like they were written by a skilled human — not a chatbot.
"""

app = FastAPI(title="VIOLET Voice Assistant API")

# Enable CORS for React frontend (Development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Mount static files (React build)
static_dir = os.path.join(os.path.dirname(__file__), "violet-web", "dist")
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

@app.get("/")
async def serve_ui():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "VIOLET Backend Running (UI not found - please build frontend)"}

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: str

def get_time():
    return datetime.now().strftime("%I:%M %p")

def get_date():
    return datetime.now().strftime("%A, %B %d, %Y")

def get_coordinates(city_name):
    """Get latitude and longitude for a city using Open-Meteo Geocoding API"""
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and data["results"]:
                return data["results"][0]["latitude"], data["results"][0]["longitude"], data["results"][0]["name"]
    except:
        pass
    return None, None, None

def get_weather_openmeteo(city="New York"):
    """Fetch weather using Open-Meteo (Free, No Key)"""
    try:
        # 1. Geocode
        lat, lon, name = get_coordinates(city)
        if not lat:
            return None # Fallback
            
        # 2. Get Weather
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m",
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh"
        }
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            temp = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            wind = current.get("wind_speed_10m")
            code = current.get("weather_code")
            
            # WMO Weather interpretation codes (http://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM)
            weather_desc = "Clear sky"
            if code in [1, 2, 3]: weather_desc = "Partly cloudy"
            elif code in [45, 48]: weather_desc = "Foggy"
            elif code in [51, 53, 55]: weather_desc = "Drizzle"
            elif code in [61, 63, 65]: weather_desc = "Rain"
            elif code in [71, 73, 75]: weather_desc = "Snow"
            elif code in [80, 81, 82]: weather_desc = "Rain showers"
            elif code in [95, 96, 99]: weather_desc = "Thunderstorm"
            
            return f"Weather in {name}:\n🌡️ {temp}°C ({weather_desc})\n💧 Humidity: {humidity}%\n💨 Wind: {wind} km/h"
    except Exception as e:
        print(f"OpenMeteo Error: {e}")
        return None
    return None

def get_weather(city="New York"):
    # Try Open-Meteo first (More reliable)
    om_response = get_weather_openmeteo(city)
    if om_response:
        return om_response

    # Fallback to wttr.in
    try:
        url = f"https://wttr.in/{city}?format=3"
        response = requests.get(url, timeout=5)
        return response.text if response.status_code == 200 else "Could not fetch weather, boss"
    except:
        return "Unable to get weather information right now, boss"

# GNews API Key - Get your free key from https://gnews.io/
GNEWS_API_KEY = "9cb63ac58cde5ddb24442031c7a74d05"

# Country name to code mapping
COUNTRY_CODES = {
    "india": "in", "indian": "in",
    "america": "us", "usa": "us", "united states": "us", "american": "us",
    "uk": "gb", "united kingdom": "gb", "britain": "gb", "british": "gb", "england": "gb",
    "australia": "au", "australian": "au",
    "canada": "ca", "canadian": "ca",
    "germany": "de", "german": "de",
    "france": "fr", "french": "fr",
    "japan": "jp", "japanese": "jp",
    "china": "cn", "chinese": "cn",
    "russia": "ru", "russian": "ru",
    "brazil": "br", "brazilian": "br",
    "italy": "it", "italian": "it",
    "spain": "es", "spanish": "es",
    "mexico": "mx", "mexican": "mx",
    "south korea": "kr", "korea": "kr", "korean": "kr",
    "singapore": "sg", "singaporean": "sg",
    "indonesia": "id", "indonesian": "id",
    "pakistan": "pk", "pakistani": "pk",
    "bangladesh": "bd", "bangladeshi": "bd",
    "sri lanka": "lk", "sri lankan": "lk",
}

def extract_country_from_command(command):
    """Extract country code from command like 'news in india' or 'headlines from america'"""
    command_lower = command.lower()
    
    # Check for country names in the command
    for country_name, country_code in COUNTRY_CODES.items():
        if country_name in command_lower:
            return country_code
    
    return None  # No specific country found, use global

def extract_city_from_command(command):
    """Extract city name from command like 'weather in chennai'"""
    command = command.lower().strip()
    
    # Regex to capture "weather in <city>", "weather for <city>", "weather at <city>"
    match = re.search(r'weather\s+(?:in|for|at|of)\s+([a-z\s]+)', command)
    if match:
        city = match.group(1)
        # Cleanup common suffix words
        ignore_words = ["today", "tomorrow", "please", "outcome", "right now", "now", "current", "currently"]
        for word in ignore_words:
            city = city.replace(f" {word}", "").replace(word, "")
        
        # Remove punctuation
        city = re.sub(r'[^\w\s]', '', city)
        return city.strip()
    return None

def analyze_sentiment(text):
    """Analyze text for basic mood/sentiment tags"""
    text = text.lower()
    
    # Sadness / Distress
    sad_keywords = ["sad", "depressed", "lonely", "unhappy", "crying", "broken", "pain", "hurt", "grief", "hopeless"]
    if any(k in text for k in sad_keywords):
        return "sad"
        
    # Tiredness / Exhaustion
    tired_keywords = ["tired", "exhausted", "sleepy", "drained", "burnout", "fatigue", "no energy", "need sleep", "need some sleep", "want to sleep", "worn out"]
    if any(k in text for k in tired_keywords):
        return "tired"
        
    return "neutral"

def get_news(country=None, max_articles=5):
    """Fetch top headlines from GNews API"""
    try:
        base_url = "https://gnews.io/api/v4/top-headlines"
        params = {
            "apikey": GNEWS_API_KEY,
            "lang": "en",
            "max": max_articles
        }
        
        if country:
            params["country"] = country
        
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            
            if not articles:
                return "No news articles found at the moment, boss."
            
            # Format headlines - structured and clean
            country_name = country.upper() if country else "World"
            headlines = [f"📰 Top Headlines - {country_name}", ""]
            
            for i, article in enumerate(articles, 1):
                title = article.get("title", "No title")
                source = article.get("source", {}).get("name", "Unknown")
                # Clean format: number, title on one line, source on next
                headlines.append(f"{i}. {title}")
                headlines.append(f"   📌 {source}")
                headlines.append("")  # Empty line between articles
            
            return "\n".join(headlines).strip()
        
        elif response.status_code == 403:
            return "News API key is invalid or expired. Please update the API key, boss."
        else:
            return f"Could not fetch news right now (Error {response.status_code}), boss."
            
    except requests.exceptions.Timeout:
        return "News request timed out, boss. Please try again."
    except Exception as e:
        return f"Unable to fetch news right now, boss. Error: {str(e)}"

def open_app(app_name):
    app_name = app_name.lower().strip()
    
    if platform.system() == "Windows":
        apps = {
            # Browsers
            "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "google chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "edge": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "microsoft edge": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "brave": "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
            
            # System Tools
            "command prompt": "cmd.exe",
            "cmd": "cmd.exe",
            "terminal": "cmd.exe",
            "powershell": "powershell.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "settings": "ms-settings:",
            "file explorer": "explorer.exe",
            "explorer": "explorer.exe",
            "run": "explorer.exe shell:::{2559a1f3-21d7-11d4-bdaf-00c04f60b9f0}",
            "device manager": "devmgmt.msc",
            "disk management": "diskmgmt.msc",
            "registry editor": "regedit.exe",
            "system info": "msinfo32.exe",
            
            # Utilities
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "snipping tool": "snippingtool.exe",
            "snip": "snippingtool.exe",
            "wordpad": "wordpad.exe",
            "character map": "charmap.exe",
            "magnifier": "magnify.exe",
            "on-screen keyboard": "osk.exe",
            
            # Microsoft Office
            "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
            "microsoft word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
            "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
            "microsoft excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
            "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
            "outlook": "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE",
            "onenote": "C:\\Program Files\\Microsoft Office\\root\\Office16\\ONENOTE.EXE",
            
            # Development
            "vscode": "code",
            "visual studio code": "code",
            "vs code": "code",
            "git bash": "C:\\Program Files\\Git\\git-bash.exe",
            
            # Media & Entertainment
            "spotify": "spotify.exe",
            "vlc": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
            "media player": "wmplayer.exe",
            "windows media player": "wmplayer.exe",
            "photos": "ms-photos:",
            "camera": "microsoft.windows.camera:",
            "movies": "mswindowsvideo:",
            "groove music": "mswindowsmusic:",
            
            # Communication
            "teams": "msteams:",
            "microsoft teams": "msteams:",
            "skype": "skype:",
            "discord": "discord:",
            "zoom": "zoom:",
            "whatsapp": "whatsapp:",
            
            # Others
            "store": "ms-windows-store:",
            "microsoft store": "ms-windows-store:",
            "xbox": "xbox:",
            "clock": "ms-clock:",
            "alarms": "ms-clock:",
            "calendar": "outlookcal:",
            "mail": "outlookmail:",
            "maps": "bingmaps:",
            "weather": "bingweather:",
            "news": "bingnews:",
        }
        
        # Exact match
        if app_name in apps:
            try:
                app_path = apps[app_name]
                import os
                # Use Windows 'start' command - most reliable method
                os.system(f'start "" "{app_path}"')
                return f"Opening {app_name} for you, boss!"
            except Exception as e:
                print(f"DEBUG: Failed to open {app_name}: {e}")
                return f"Sorry boss, I couldn't open {app_name}"
        
        # Fuzzy match / system command fallback
        try:
            import os
            os.system(f'start "" "{app_name}"')
            return f"Attempting to launch {app_name}, boss!"
        except Exception as e:
            print(f"DEBUG: Fallback failed for {app_name}: {e}")
            
    return f"Sorry boss, I couldn't find {app_name}"

def search_web(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching Google for '{query}' for you, boss!"

def play_youtube(query):
    """Play a song or video on YouTube using pywhatkit"""
    try:
        import pywhatkit
        pywhatkit.playonyt(query)
        return f"🎵 Playing '{query}' on YouTube for you, boss!"
    except Exception as e:
        # Fallback to standard browser search if pywhatkit fails
        import urllib.parse
        import webbrowser
        encoded_query = urllib.parse.quote(query)
        youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        webbrowser.open(youtube_url)
        return f"🎵 I couldn't auto-play, so I opened the search results for '{query}'."

# ==========================================
# IoT DEVICE CONTROL FUNCTIONS
# ==========================================

def control_iot_device(device, action):
    """Send HTTP request to ESP32 to control a relay"""
    device = device.lower().strip()
    action = action.lower().strip()
    
    if device not in IOT_DEVICES:
        return f"Sorry boss, I don't recognize the device '{device}'. Available devices: Light, Fan."
    
    device_info = IOT_DEVICES[device]
    relay = device_info["relay"]
    device_name = device_info["name"]
    
    if action not in ["on", "off"]:
        return f"Sorry boss, I can only turn devices ON or OFF."
    
    try:
        url = f"http://{ESP32_IP}:{ESP32_PORT}/{relay}/{action}"
        print(f"DEBUG IoT: Sending request to {url}")
        response = requests.get(url, timeout=IOT_TIMEOUT)
        
        if response.status_code == 200:
            # Update local cache
            IOT_DEVICES[device]["state"] = (action == "on")
            state_emoji = "✅" if action == "on" else "❌"
            return f"{state_emoji} {device_name} turned {action.upper()} successfully, boss!"
        else:
            return f"ESP32 responded with error code {response.status_code}, boss."
            
    except requests.exceptions.ConnectionError:
        return f"Could not connect to ESP32 at {ESP32_IP}. Make sure it's powered on and connected to the same Wi-Fi network, boss."
    except requests.exceptions.Timeout:
        return f"ESP32 timed out. It might be offline or unreachable, boss."
    except Exception as e:
        return f"IoT Error: {str(e)}"

def get_iot_status():
    """Fetch current device states from ESP32"""
    try:
        url = f"http://{ESP32_IP}:{ESP32_PORT}/status"
        response = requests.get(url, timeout=IOT_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            # Update local cache
            IOT_DEVICES["light"]["state"] = (data.get("relay1") == "ON")
            IOT_DEVICES["fan"]["state"] = (data.get("relay2") == "ON")
            
            light_status = "ON 🟢" if IOT_DEVICES["light"]["state"] else "OFF 🔴"
            fan_status = "ON 🟢" if IOT_DEVICES["fan"]["state"] else "OFF 🔴"
            
            return f"🏠 Smart Home Status\n\n💡 Light: {light_status}\n🌀 Fan: {fan_status}"
        else:
            return "Could not fetch device status from ESP32, boss."
            
    except requests.exceptions.ConnectionError:
        return f"ESP32 is offline or unreachable at {ESP32_IP}, boss. Make sure it's connected."
    except requests.exceptions.Timeout:
        return "ESP32 timed out while fetching status, boss."
    except Exception as e:
        return f"IoT Status Error: {str(e)}"

def parse_iot_command(command):
    """Parse IoT voice commands and return (device, action) or None"""
    command = command.lower().strip()
    
    # Detect action
    action = None
    if any(w in command for w in ["turn on", "switch on", "power on", "enable", "start"]):
        action = "on"
    elif any(w in command for w in ["turn off", "switch off", "power off", "disable", "stop"]):
        action = "off"
    
    if not action:
        # Check shorthand: "light on", "fan off"
        if command.endswith(" on"):
            action = "on"
        elif command.endswith(" off"):
            action = "off"
    
    if not action:
        return None
    
    # Detect device
    device = None
    if any(w in command for w in ["light", "lights", "lamp", "bulb", "led", "relay 1", "relay1"]):
        device = "light"
    elif any(w in command for w in ["fan", "fans", "motor", "relay 2", "relay2"]):
        device = "fan"
    
    if device and action:
        return (device, action)
    return None

def set_alarm(time_str):
    """Set an alarm using Windows Clock app"""
    import os
    import re
    
    # Parse time from various formats
    time_str = time_str.lower().strip()
    
    # Try to extract time pattern (e.g., "5:30", "5.30", "530", "5 30")
    time_match = re.search(r'(\d{1,2})[:\.\s]?(\d{2})?\s*(am|pm)?', time_str)
    
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        period = time_match.group(3)
        
        # Convert to 12-hour format for display
        if period == 'pm' and hour < 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
            
        # Format time for display
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
        display_period = 'AM' if hour < 12 else 'PM'
        time_display = f"{display_hour}:{minute:02d} {display_period}"
        
        # Open Windows Alarms & Clock app
        os.system('start ms-clock:')
        
        return f"⏰ Opening Windows Clock app! Please set your alarm for {time_display}, boss. The app is ready for you!"
    else:
        # Just open the clock app
        os.system('start ms-clock:')
        return f"⏰ Opening Windows Clock app for you, boss! Set your alarm there."

def set_reminder(task, time_str=None):
    """Add a reminder to the list"""
    import re
    from datetime import datetime
    
    reminder = {
        "task": task,
        "time": time_str if time_str else "No specific time",
        "created": datetime.now().strftime("%I:%M %p, %b %d")
    }
    
    REMINDERS.append(reminder)
    
    # Also open Clock app for setting an actual alert
    os.system('start ms-clock:')
    
    if time_str:
        return f"📝 Reminder set!\n\nTask: {task}\nTime: {time_str}\n\nI've also opened the Clock app so you can set an alert!"
    else:
        return f"📝 Reminder noted!\n\nTask: {task}\n\nI've also opened the Clock app if you want to set an alert."

def get_reminders():
    """Get all reminders"""
    if not REMINDERS:
        return "📋 You have no reminders set, boss."
    
    result = "📋 Your Reminders:\n\n"
    for i, r in enumerate(REMINDERS, 1):
        result += f"{i}. {r['task']}\n"
        result += f"   ⏰ {r['time']}\n"
        result += f"   📅 Set on: {r['created']}\n\n"
    
    return result.strip()

def clear_reminders():
    """Clear all reminders"""
    REMINDERS.clear()
    return "🗑️ All reminders cleared, boss!"

def translate_text(text, target_language="english", source_language=None):
    """Translate text using Gemini AI with dynamic model discovery"""
    try:
        client = genai.Client(api_key=API_KEY)
        
        # Build translation prompt
        if source_language:
            prompt = f"Translate the following {source_language} text to {target_language}. Only provide the translation, no explanations:\n\n{text}"
        else:
            prompt = f"Translate the following text to {target_language}. Detect the source language automatically. Only provide the translation, no explanations:\n\n{text}"
        
        # Dynamic Model Discovery (same as ask_gemini)
        all_models = list(client.models.list())
        valid_models = [
            m.name for m in all_models 
            if 'gemini' in m.name and 'embedding' not in m.name
        ]
        
        # Priority list
        priorities = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro', 'gemini-pro']
        
        sorted_models = []
        for p in priorities:
            matches = [m for m in valid_models if p in m]
            for m in matches:
                if m not in sorted_models:
                    sorted_models.append(m)
        
        for m in valid_models:
            if m not in sorted_models:
                sorted_models.append(m)
        
        if not sorted_models:
            return "Sorry boss, no AI models available for translation."
        
        # Try models
        for model_name in sorted_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                translation = response.text.strip()
                return f"🌐 Translation ({target_language.title()}):\n\n{translation}"
            except:
                continue
        
        return "Sorry boss, I couldn't translate that. No working model found."
        
    except Exception as e:
        return f"Sorry boss, I couldn't translate that. Error: {str(e)}"

def calculate_math(command):
    """
    Parses and calculates math expressions from natural language.
    Supports basic arithmetic and common math functions.
    """
    try:
        # Pre-process command to more standard math notation
        # Remove common prefixes
        prompts = ["calculate", "solve", "what is", "how much is", "math", "evaluate"]
        cleaned_cmd = command.lower()
        for p in prompts:
            if cleaned_cmd.startswith(p):
                cleaned_cmd = cleaned_cmd.replace(p, "").strip()
        
        # Replace natural language operators
        replacements = {
            "plus": "+",
            "minus": "-",
            "times": "*",
            "multiplied by": "*",
            "x": "*", # CAUTION: 'x' might be a variable, but mostly 'times' in voice
            "divided by": "/",
            "over": "/",
            "to the power of": "**",
            "squared": "**2",
            "cubed": "**3",
            "square root of": "sqrt",
            "root": "sqrt",
            "pi": str(math.pi),
            "percent of": "* 0.01 *",
            "mod": "%",
            "modulo": "%"
        }
        
        for word, sym in replacements.items():
            cleaned_cmd = cleaned_cmd.replace(word, sym)
            
        # Clean up remaining text to allow only math-safe characters
        # Allow numbers, operators, parens, and specific functions
        allowed_chars = r"0-9\+\-\*\/\%\.\(\)\s"
        # We need to allow specific function names like 'sqrt', 'sin', 'cos', 'tan', 'log'
        # So we can't just strictly regex filter chars easily without breaking functions.
        # Instead, let's trust the replacements and eval carefully with a whitelist.
        
        # Basic sanity check: reject if it contains letters not in our whitelist
        whitelist_funcs = ["sqrt", "sin", "cos", "tan", "log", "exp", "pow", "abs", "round", "ceil", "floor"]
        
        # Construct a safe environment
        safe_dict = {k: getattr(math, k) for k in whitelist_funcs if hasattr(math, k)}
        safe_dict["__builtins__"] = None
        
        # Evaluate
        result = eval(cleaned_cmd, safe_dict)
        
        # Format result
        if isinstance(result, float):
             return f"The answer is {round(result, 4)}." 
        return f"The answer is {result}."
        
    except Exception as e:
        return f"I couldn't calculate that. {str(e)}"

def ask_gemini(question, mood="neutral"):
    try:
        client = genai.Client(api_key=API_KEY)
        
        # Dynamic Model Discovery
        all_models = list(client.models.list())
        
        # Filter for models (heuristic: contains 'gemini' and not 'embedding')
        valid_models = [
            m.name for m in all_models 
            if 'gemini' in m.name and 'embedding' not in m.name
        ]
        
        # Priority list
        priorities = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-1.0-pro',
            'gemini-pro'
        ]
        
        # Sort valid models by priority
        sorted_models = []
        for p in priorities:
            # Find all matching models for this priority (e.g. all flash variants)
            matches = [m for m in valid_models if p in m]
            # Add to list if not already there
            for m in matches:
                if m not in sorted_models:
                    sorted_models.append(m)
        
        # Add remaining valid models that weren't in priority list
        for m in valid_models:
             if m not in sorted_models:
                 sorted_models.append(m)

        if not sorted_models:
             return "Sorry boss, no valid AI models found for this key."

        # Adapt System Prompt based on Mood
        system_prompt = VIOLET_PERSONALITY
        if mood == "sad":
             system_prompt += "\n\nCURRENT CONTEXT: The user is feeling SAD. Respond gently, warmly, and offer emotional support. Avoid being too technical or robotic. Be a comforting friend."
        elif mood == "tired":
             system_prompt += "\n\nCURRENT CONTEXT: The user is feeling TIRED. Keep your response brief. Gently suggest they get some rest or sleep. Ask if they want you to set a sleep reminder."

        # Try models in order
        for model_name in sorted_models:
            print(f"DEBUG: Trying model {model_name}...")
            try:
                # Build context (same as before)
                history_text = "\n".join([f"{role}: {msg}" for role, msg in CONVERSATION_HISTORY])
                full_prompt = f"{system_prompt}\n\nCONVERSATION HISTORY:\n{history_text}\n\nCURRENT REQUEST:\nUser says: {question}\n\nRespond as VIOLET (concise, natural, helpful):"

                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                print(f"DEBUG: Success with {model_name}")
                return response.text
            except Exception as e:
                print(f"DEBUG: Failed with {model_name}: {e}")
                continue # Try next model
        
        return "Sorry boss, I tried all AI models but they are having trouble. Please check the API Key."

    except Exception as e:
        print(f"DEBUG: Critical Error: {e}")
        return f"Sorry boss, something went wrong: {str(e)}"

CONTACTS_FILE = os.path.join(os.path.dirname(__file__), "contacts.json")

def load_contacts():
    try:
        if os.path.exists(CONTACTS_FILE):
            with open(CONTACTS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"DEBUG: Error loading contacts: {e}")
    return {}

def save_contact(name, phone):
    contacts = load_contacts()
    # Normalize name and ensure phone is string
    name_key = name.lower().strip()
    contacts[name_key] = str(phone).strip()
    try:
        with open(CONTACTS_FILE, 'w') as f:
            json.dump(contacts, f, indent=4)
        return f"Saved {name} as {phone}, boss!"
    except Exception as e:
        return f"Error saving contact: {str(e)}"

def send_whatsapp_message(contact_name, message):
    contacts = load_contacts()
    phone = contacts.get(contact_name.lower().strip())
    
    if not phone:
        return f"Sorry boss, I don't have a phone number for {contact_name}. You can say 'save {contact_name} as [phone number]' to add them."
    
    try:
        # Normalize phone number
        phone = "".join(c for c in phone if c.isdigit())
        
        # If it's a 10-digit number (common in India), prepend +91
        if len(phone) == 10:
            phone = f"+91{phone}"
        elif not phone.startswith('+'):
            phone = f"+{phone}"
            
        print(f"DEBUG: Normalized phone number: {phone}")
        
        # WhatsApp Desktop URI protocol
        import urllib.parse
        encoded_msg = urllib.parse.quote(message)
        # Use 'whatsapp://send?phone=...' to trigger the native app
        whatsapp_url = f"whatsapp://send?phone={phone}&text={encoded_msg}"
        
        print(f"DEBUG: Triggering WhatsApp Desktop: {whatsapp_url}")
        webbrowser.open(whatsapp_url)
        
        # New: Auto-send the message by pressing 'enter' in a separate thread
        def auto_send():
            time.sleep(5) # Increased delay to 5 seconds
            pyautogui.press('enter')
            time.sleep(0.5)
            pyautogui.press('enter') # Double tap for reliability
            print("DEBUG: Auto-sent WhatsApp message (pressed enter twice)")
            
        threading.Thread(target=auto_send, daemon=True).start()
        
        return f"Opening WhatsApp Desktop to send your message to {contact_name}, boss!"
    except Exception as e:
        return f"Error opening WhatsApp Desktop: {str(e)}"

def process_command(command):
    command_str = command.strip()
    command_lower = command_str.lower()
    
    # DEBUG: Print what we received
    print(f"DEBUG: Received command: '{command_lower}'")
    
    response = ""

    # WhatsApp - Messaging (check BEFORE greeting to avoid collision)
    is_whatsapp = any(w in command_lower for w in ["whatsapp", "on whatsapp"])
    is_msg_intent = any(w in command_lower for w in ["send", "message", "saying", "sayy", "say"])
    
    print(f"DEBUG: is_whatsapp={is_whatsapp}, is_msg_intent={is_msg_intent}")
    
    if is_whatsapp and is_msg_intent:
        # Extract contact and message
        # Example: "send a message to Thamim on whatsapp saying hello" or "sayy 'Hi ...' to him"
        trigger_word = None
        if "saying" in command_lower:
            trigger_word = "saying"
        elif "sayy" in command_lower:
            trigger_word = "sayy"
        elif "say" in command_lower:
             trigger_word = "say"

        if trigger_word:
            parts = command_lower.split(trigger_word)
            msg = parts[1].strip().strip('"').strip("'")
            # Clean up contact string
            contact_part = parts[0]
            # Replace common filler words to extract the contact name
            contact_str = contact_part.replace("send", "").replace("a message to", "").replace("the person", "").replace("on whatsapp", "").replace("whatsapp", "").replace("message", "").replace("hii", "").replace("hi", "").strip().strip('"').strip("'")
            
            # If contact_str is empty or "him"/"her", try to find if a contact name was mentioned earlier or in history
            if contact_str in ["him", "her", "them", ""]:
                response = "I'm not sure who to send the message to, boss. Could you specify the name?"
            else:
                response = send_whatsapp_message(contact_str, msg)
        else:
            response = "What message would you like me to send on WhatsApp, boss? (Please include 'saying [your message]')"
    
    # Save Contact
    elif "save" in command_lower and "as" in command_lower and not any(w in command_lower for w in ["remind", "alarm"]):
        # Example: "save loosu thamim as +911234567890"
        parts = command_lower.replace("save", "").split("as")
        if len(parts) == 2:
            name = parts[0].strip()
            phone = parts[1].strip().replace(" ", "")
            response = save_contact(name, phone)
        else:
            response = "How should I save this contact, boss? Please say 'save [name] as [number]'"

    # Regex for precise greeting matching (exclude if action-oriented)
    elif re.search(r'\b(hello|hi|hey)\b', command_lower) and not any(w in command_lower for w in ["translate", "message", "whatsapp", "search", "open", "launch"]):
        response = "Hello boss! I'm VIOLET, your personal assistant. How can I help you today?"
    
    # Identity
    elif any(w in command_lower for w in ["who are you", "what is your name"]):
        response = "I'm VIOLET, boss! Your advanced AI assistant."
    
    # Time
    elif re.search(r'\btime\b', command_lower):
        response = f"It's {get_time()}, boss!"
    
    # Weather (Check BEFORE News/Date because "today's weather" or "update me with weather" shouldn't trigger those)
    elif "weather" in command_lower:
        city = extract_city_from_command(command_str)
        if city:
            response = get_weather(city)
        else:
            response = get_weather() # Default to New York if no city found
    
    # News / Headlines (check BEFORE date - "today's news" contains "today")
    elif any(w in command_lower for w in ["news", "headlines", "update me", "what's happening"]):
        country = extract_country_from_command(command_str)
        response = get_news(country=country)
    
    # Date (exclude if news-related)
    elif re.search(r'\b(date|day|today)\b', command_lower) and "news" not in command_lower:
        response = f"Today is {get_date()}, boss!"
    
    # Open apps
    elif command_lower.startswith("open ") or command_lower.startswith("launch "):
        app_name = command_lower.replace("open ", "").replace("launch ", "").strip()
        response = open_app(app_name)
    
    # Shutdown
    elif "shutdown" in command_lower and ("laptop" in command_lower or "pc" in command_lower):
        try:
            subprocess.Popen(["shutdown", "/s", "/t", "5"])
            response = "Shutting down the laptop in 5 seconds, boss. Goodbye!"
        except Exception as e:
            response = f"Error shutting down: {str(e)}"
            
    # IoT Device Control (voice commands)
    elif any(w in command_lower for w in ["turn on", "turn off", "switch on", "switch off"]) and any(d in command_lower for d in ["light", "lights", "lamp", "bulb", "led", "fan", "fans", "motor", "relay"]):
        iot_result = parse_iot_command(command_lower)
        if iot_result:
            device, action = iot_result
            response = control_iot_device(device, action)
        else:
            response = "Sorry boss, I couldn't understand that IoT command. Try 'turn on the light' or 'turn off the fan'."
    
    # IoT Status Check
    elif any(w in command_lower for w in ["device status", "iot status", "smart home status", "home status", "device state", "show devices"]):
        response = get_iot_status()
    
    # Web search
    elif command_lower.startswith("search ") or command_lower.startswith("google "):
        query = command_lower.replace("search ", "").replace("google ", "").strip()
        response = search_web(query)
    
    # YouTube - play music/videos
    elif "play" in command_lower and ("youtube" in command_lower or "yt" in command_lower):
        # Extract song/video name - remove common words
        query = command_lower
        for word in ["play", "on youtube", "in youtube", "on yt", "in yt", "youtube", "yt", "song", "video", "music"]:
            query = query.replace(word, "")
        query = query.strip()
        if query:
            response = play_youtube(query)
        else:
            response = "What would you like me to play on YouTube, boss?"
    
    # Show reminders
    elif any(w in command_lower for w in ["show reminders", "my reminders", "list reminders", "what are my reminders"]):
        response = get_reminders()
    
    # Clear reminders
    elif any(w in command_lower for w in ["clear reminders", "delete reminders", "remove reminders"]):
        response = clear_reminders()
    
    # Set reminder (NOT alarm - "remind me that" vs "remind me at")
    elif "remind me" in command_lower and "at" not in command_lower:
        # Extract task from "remind me that..." or "remind me to..."
        task = command_lower
        for word in ["remind me that", "remind me to", "remind me"]:
            task = task.replace(word, "")
        task = task.strip()
        
        # Try to extract time if mentioned
        time_match = re.search(r'at\s+(\d{1,2}[:\.]?\d{0,2}\s*(am|pm)?)', task)
        time_str = None
        if time_match:
            time_str = time_match.group(1)
            task = task.replace(time_match.group(0), "").strip()
        
        if task:
            response = set_reminder(task, time_str)
        else:
            response = "What would you like me to remind you about, boss?"
    
    # Reminder with time (e.g., "remind me at 5 PM about meeting")
    elif "remind me" in command_lower and "at" in command_lower:
        # Extract time
        time_match = re.search(r'at\s+(\d{1,2}[:\.]?\d{0,2}\s*(am|pm)?)', command_lower)
        time_str = time_match.group(1) if time_match else None
        
        # Extract task
        task = command_lower
        for word in ["remind me", "about", "that", "to"]:
            task = task.replace(word, "")
        if time_match:
            task = task.replace(time_match.group(0), "")
        task = task.strip()
        
        if task:
            response = set_reminder(task, time_str)
        else:
            response = "What would you like me to remind you about, boss?"
    
    # Alarm / Timer (without "remind me" - that's handled above)
    elif any(w in command_lower for w in ["set alarm", "set an alarm", "alarm for", "alarm at", "wake me"]):
        # Extract time from command
        time_str = command_lower
        for word in ["set alarm", "set an alarm", "alarm for", "alarm at", "wake me up at", "wake me at", "for", "at"]:
            time_str = time_str.replace(word, "")
        response = set_alarm(time_str.strip())
    
    # Translation
    elif any(w in command_lower for w in ["translate", "in english", "in tamil", "in hindi", "to english", "to tamil", "to hindi", "what is", "how do you say", "meaning of"]):
        # Determine target language
        target_lang = "english"  # default
        if "tamil" in command_lower or "தமிழ்" in command_lower:
            if "to tamil" in command_lower or "in tamil" in command_lower:
                target_lang = "tamil"
            else:
                target_lang = "english"  # translating FROM tamil TO english
        elif "hindi" in command_lower or "हिंदी" in command_lower:
            if "to hindi" in command_lower or "in hindi" in command_lower:
                target_lang = "hindi"
            else:
                target_lang = "english"  # translating FROM hindi TO english
        elif "to english" in command_lower or "in english" in command_lower:
            target_lang = "english"
        
        # Extract text to translate
        text_to_translate = command_lower
        for word in ["translate", "to english", "in english", "to tamil", "in tamil", "to hindi", "in hindi", 
                     "what is", "how do you say", "meaning of", "tell me", "say", "the word"]:
            text_to_translate = text_to_translate.replace(word, "")
        text_to_translate = text_to_translate.strip()
        
        if text_to_translate:
            response = translate_text(text_to_translate, target_lang)
        else:
            response = "What would you like me to translate, boss?"

    # Math
    elif any(trigger in command_lower for trigger in ["calculate", "solve", "plus", "minus", "divided by", "multiplied by", "square root"]):
        if "weather" in command_lower: # Avoid false positive "calculate the weather" (unlikely but safe)
             response = ask_gemini(command_str)
        else:
             response = calculate_math(command_str)


    # Default: Ask Gemini AI (with history)
    else:
        # Detect Mood first
        mood = analyze_sentiment(command_str)
        
        # One last check for math that starts with "what is" but contains math ops
        if command_lower.startswith("what is") and any(op in command_lower for op in ["+", "-", "*", "/", "plus", "minus", "times"]):
             response = calculate_math(command_str)
        else:
             response = ask_gemini(command_str, mood=mood)
    
    # Update Memory
    CONVERSATION_HISTORY.append(("User", command_str))
    CONVERSATION_HISTORY.append(("Violet", response))
    
    return response

@app.get("/")
async def root():
    return {"message": "VIOLET Voice Assistant API is running!", "status": "active"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    response_text = process_command(request.message)
    
    return ChatResponse(
        response=response_text,
        timestamp=datetime.now().isoformat()
    )

@app.get("/health")
async def health():
    return {"status": "healthy", "assistant": "VIOLET"}


# ==========================================
# IoT REST API ENDPOINTS
# ==========================================

class IoTControlRequest(BaseModel):
    device: str
    action: str

@app.get("/api/iot/status")
async def iot_status():
    """Get current IoT device states"""
    try:
        url = f"http://{ESP32_IP}:{ESP32_PORT}/status"
        resp = requests.get(url, timeout=IOT_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            # Update local cache
            IOT_DEVICES["light"]["state"] = (data.get("relay1") == "ON")
            IOT_DEVICES["fan"]["state"] = (data.get("relay2") == "ON")
            return {
                "connected": True,
                "esp32_ip": ESP32_IP,
                "devices": {
                    "light": {"name": "Light", "state": IOT_DEVICES["light"]["state"]},
                    "fan":   {"name": "Fan",   "state": IOT_DEVICES["fan"]["state"]},
                }
            }
    except:
        pass
    
    # Return cached state if ESP32 is unreachable
    return {
        "connected": False,
        "esp32_ip": ESP32_IP,
        "devices": {
            "light": {"name": "Light", "state": IOT_DEVICES["light"]["state"]},
            "fan":   {"name": "Fan",   "state": IOT_DEVICES["fan"]["state"]},
        }
    }

@app.post("/api/iot/control")
async def iot_control(request: IoTControlRequest):
    """Control an IoT device"""
    result = control_iot_device(request.device, request.action)
    return {
        "message": result,
        "device": request.device,
        "action": request.action,
        "success": "successfully" in result.lower()
    }


# ==========================================
# CLAP DETECTION SYSTEM
# ==========================================
class ClapDetector:
    def __init__(self):
        self.running = False
        self.thread = None
        self.stream = None
        self.clap_times = []
        self.lock = threading.Lock()
        self.loop = None # Capture event loop for async broadcast
        
    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        print("👏 Clap Detector Started! Clap 3 times to play 'Sao Paulo'!")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            
    def _trigger_action(self):
        print("🎉 3 CLAPS DETECTED! BROADCASTING AND PLAYING!")
        
        # Broadcast event to frontend via WebSocket
        if self.loop:
            try:
                asyncio.run_coroutine_threadsafe(manager.broadcast("clap_detected"), self.loop)
            except Exception as e:
                print(f"Broadcast error: {e}")
        
        # Wait 2 seconds so user can see the message
        time.sleep(2.0)
        
        # Trigger the action
        play_youtube("Sao Paulo Song")

    def _listen_loop(self):
        try:
            import sounddevice as sd
            
            RATE = 44100
            THRESHOLD = 2500  # Lowered sensitivity to 2500 (was 4000)
            
            def audio_callback(indata, frames, time_info, status):
                if not self.running:
                    raise sd.CallbackStop()
                
                audio_data = indata.flatten()
                peak = np.max(np.abs(audio_data))
                
                # Calculate Crest Factor (Impulsiveness)
                # RMS (Average energy)
                rms = np.sqrt(np.mean(audio_data.astype(np.float32)**2))
                crest_factor = peak / rms if rms > 1e-6 else 0
                
                # LOG ALL SIGNIFICANT SOUNDS for debugging
                if peak > 1500:
                    print(f"DEBUG: Peak={peak:.0f}, Crest={crest_factor:.2f}")

                # A true clap is LOUD and IMPULSIVE (High Crest Factor)
                # Typical speech has crest factor 3-5. Claps are usually > 8-10.
                if peak > THRESHOLD and crest_factor > 7.0:
                    now = time.time()
                    with self.lock:
                        # Debounce 0.15s
                        if not self.clap_times or (now - self.clap_times[-1] > 0.15):
                            # Reset if too much time passed (gap > 2.0s)
                            if self.clap_times and (now - self.clap_times[-1] > 2.0):
                                print(f"DEBUG: Resetting clap count (Gap was {now - self.clap_times[-1]:.2f}s)")
                                self.clap_times = []
                            
                            self.clap_times.append(now)
                            print(f"👏 Clap {len(self.clap_times)} Detected!")
                            print(f"   [Details: Peak={peak:.0f}, Crest={crest_factor:.1f}]")
                            
                            if len(self.clap_times) == 3:
                                # Run blocking action logic in separate thread
                                threading.Thread(target=self._trigger_action).start()
                                self.clap_times = []
                            else:
                                print(f"👉 Need {3 - len(self.clap_times)} more claps within 2 seconds...")
            
            print(f"DEBUG: Mic Open for Claps (SoundDevice). Threshold: {THRESHOLD}")
            
            with sd.InputStream(channels=1, samplerate=RATE, dtype='int16', callback=audio_callback):
                while self.running:
                    sd.sleep(100)
                    
        except Exception as e:
            print(f"Failed to start Clap Detector: {e}")

# Initialize detector
clap_detector = ClapDetector()

@app.on_event("startup")
async def startup_event():
    # Capture the running event loop for thread-safe async calls
    clap_detector.loop = asyncio.get_running_loop()
    # Start clap detection
    # clap_detector.start()

@app.on_event("shutdown")
async def shutdown_event():
    clap_detector.stop()

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("VIOLET Backend Server Starting (HTTPS)...")
    print("=" * 60)
    # HTTPS Configuration
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001
    )
