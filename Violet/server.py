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

# Force UTF-8 encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configuration
import re
import math
from collections import deque

# Configuration
API_KEY = 'AIzaSyDKlnBROOL3temn2-rYJU4KKcWQQqqu844'

# Advanced Memory
CONVERSATION_HISTORY = deque(maxlen=10)  # Stores last 10 interactions
REMINDERS = []  # Store reminders as list of dicts: {"task": str, "time": str, "created": datetime}

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

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://localhost:5173",
        "http://127.0.0.1:5173",
        "https://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def process_command(command):
    command_str = command.strip()
    command_lower = command_str.lower()
    
    # DEBUG: Print what we received
    print(f"DEBUG: Received command: '{command_lower}'")
    
    response = ""

    # Regex for precise greeting matching (exclude if translating)
    if re.search(r'\b(hello|hi|hey)\b', command_lower) and not any(w in command_lower for w in ["translate", "in tamil", "in hindi", "in english", "to tamil", "to hindi", "to english"]):
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
            THRESHOLD = 4000  # Lowered sensitivity further (was 6000)
            
            def audio_callback(indata, frames, time_info, status):
                if not self.running:
                    raise sd.CallbackStop()
                
                if status:
                    print(f"Audio Status: {status}")
                
                audio_data = indata.flatten()
                peak = np.max(np.abs(audio_data))
                
                # Debug print for any significant sound
                if peak > 2000:
                    print(f"DEBUG: Sound detected. Peak: {peak}")
                
                if peak > THRESHOLD:
                    now = time.time()
                    with self.lock:
                        # Debounce 0.15s
                        if not self.clap_times or (now - self.clap_times[-1] > 0.15):
                            # Reset if too much time passed (gap > 3.0s)
                            if self.clap_times and (now - self.clap_times[-1] > 3.0):
                                print(f"DEBUG: Resetting clap count (Time gap too large: {now - self.clap_times[-1]:.2f}s)")
                                self.clap_times = []
                            
                            self.clap_times.append(now)
                            print(f"👏 Clap {len(self.clap_times)} Detected! (Peak: {peak})")
                            
                            if len(self.clap_times) == 3:
                                # Run blocking action logic in separate thread
                                threading.Thread(target=self._trigger_action).start()
                                self.clap_times = []
            
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
    clap_detector.start()

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
