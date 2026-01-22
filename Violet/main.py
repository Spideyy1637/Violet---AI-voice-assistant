import pyttsx3
from datetime import datetime
import requests
import webbrowser
import subprocess
import platform
from google import genai
import io
import wave
import json

# Try to import sounddevice for microphone access (works with Python 3.14)
try:
    import sounddevice as sd
    import numpy as np
    VOICE_INPUT_AVAILABLE = True
except ImportError:
    VOICE_INPUT_AVAILABLE = False
    print("⚠️ Voice input not available. Install: pip install sounddevice numpy")

def record_audio(duration=5, sample_rate=16000):
    """Record audio from microphone using sounddevice"""
    print("\n🎤 Listening... (speak now)")
    try:
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()  # Wait until recording is finished
        return recording, sample_rate
    except Exception as e:
        print(f"❌ Recording error: {e}")
        return None, None

def audio_to_wav_bytes(audio_data, sample_rate):
    """Convert numpy audio array to WAV bytes"""
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    buffer.seek(0)
    return buffer.read()

def transcribe_with_google(audio_bytes):
    """Send audio to Google Speech Recognition API"""
    url = "http://www.google.com/speech-api/v2/recognize?output=json&lang=en-US&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
    headers = {"Content-Type": "audio/l16; rate=16000"}
    
    try:
        response = requests.post(url, data=audio_bytes, headers=headers, timeout=10)
        # Parse the response (Google returns multiple JSON objects)
        for line in response.text.strip().split('\n'):
            if line:
                try:
                    result = json.loads(line)
                    if 'result' in result and len(result['result']) > 0:
                        alternatives = result['result'][0].get('alternative', [])
                        if alternatives:
                            return alternatives[0].get('transcript', '')
                except json.JSONDecodeError:
                    continue
        return None
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None

def listen():
    """Listen to microphone and convert speech to text"""
    if not VOICE_INPUT_AVAILABLE:
        print("❌ Voice input not available. Please type your message.")
        return None
    
    try:
        # Record audio for 5 seconds
        audio_data, sample_rate = record_audio(duration=5, sample_rate=16000)
        if audio_data is None:
            return None
        
        # Check if there's actual audio (not just silence)
        if np.max(np.abs(audio_data)) < 100:
            print("⏰ No speech detected, try again...")
            return None
        
        print("⏳ Processing speech...")
        
        # Convert to WAV and send to Google
        wav_bytes = audio_to_wav_bytes(audio_data, sample_rate)
        text = transcribe_with_google(wav_bytes)
        
        if text:
            print(f"👤 You said: {text}")
            return text
        else:
            print("❌ Could not understand audio, please try again...")
            return None
            
    except OSError as e:
        print(f"❌ Microphone error: {e}")
        print("💡 Make sure you have a microphone connected.")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Initialize text-to-speech with female voice
engine = pyttsx3.init()

# Set female voice (Zira on Windows, or search for female voice)
voices = engine.getProperty('voices')
female_voice = None
for voice in voices:
    # Look for female voice - commonly "Zira" on Windows or voices with "female" in properties
    if 'zira' in voice.name.lower() or 'female' in voice.name.lower() or 'woman' in voice.name.lower():
        female_voice = voice.id
        break
    # On Windows, the second voice is usually female
    if voices.index(voice) == 1:
        female_voice = voice.id

if female_voice:
    engine.setProperty('voice', female_voice)

# Adjust for younger sounding voice (slightly faster, higher pitch effect)
engine.setProperty('rate', 165)  # Slightly faster for younger voice
engine.setProperty('volume', 1.0)

def speak(text):
    """Convert text to speech"""
    try:
        print(f"\n🤖 Assistant: {text}\n")
        engine.say(text)
        engine.runAndWait()
    except:
        print(f"\n🤖 Assistant: {text}\n")

def get_time():
    return datetime.now().strftime("%I:%M %p")

def get_date():
    return datetime.now().strftime("%A, %B %d, %Y")

def get_weather(city="Chennai"):
    try:
        url = f"https://wttr.in/{city}?format=3"
        response = requests.get(url, timeout=5)
        return response.text if response.status_code == 200 else "Could not fetch weather"
    except:
        return "Unable to get weather information"

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
    """Extract country code from command like 'news in india'"""
    command_lower = command.lower()
    for country_name, country_code in COUNTRY_CODES.items():
        if country_name in command_lower:
            return country_code
    return None

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
                return "No news articles found at the moment."
            
            # Format headlines for voice
            headlines = []
            for i, article in enumerate(articles, 1):
                title = article.get("title", "No title")
                headlines.append(f"{i}. {title}")
            
            country_text = f" from {country.upper()}" if country else ""
            header = f"Here are today's top headlines{country_text}:\n"
            return header + "\n".join(headlines)
        
        elif response.status_code == 403:
            return "News API key is invalid. Please update the API key."
        else:
            return f"Could not fetch news right now."
            
    except:
        return "Unable to fetch news right now."

def open_app(app_name):
    app_name = app_name.lower().strip()
    
    if platform.system() == "Windows":
        apps = {
            "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "edge": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        }
        if app_name in apps:
            try:
                subprocess.Popen(apps[app_name])
                return f"Opening {app_name}"
            except:
                return f"Could not open {app_name}"
    return f"App {app_name} not found"

def search_web(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching Google for {query}"

def ask_gemini(api_key, question):
    try:
        client = genai.Client(api_key=api_key)
        # Try different models in order (using available models from your API)
        models_to_try = ['gemini-2.0-flash-001', 'gemini-2.5-flash', 'gemini-flash-latest']
        
        last_error = None
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=question
                )
                return response.text[:200]
            except Exception as model_error:
                last_error = model_error
                continue
        
        return f"Model not available. Last error: {last_error}"
    except Exception as e:
        return f"Error: {str(e)}"

def process_command(command, api_key):
    command = command.lower().strip()
    
    if any(w in command for w in ["time", "what time"]):
        return f"The time is {get_time()}"
    elif any(w in command for w in ["date", "today", "what day"]):
        return f"Today is {get_date()}"
    elif any(w in command for w in ["weather", "temperature"]):
        return get_weather()
    elif any(w in command for w in ["news", "headlines", "update me", "what's happening"]):
        country = extract_country_from_command(command)
        return get_news(country=country)
    elif any(w in command for w in ["open", "launch"]):
        for app in ["chrome", "firefox", "notepad", "calculator", "edge"]:
            if app in command:
                return open_app(app)
    elif any(w in command for w in ["search", "find", "look up"]):
        query = command.replace("search", "").replace("find", "").strip()
        return search_web(query)
    elif any(w in command for w in ["hello", "hi", "hey"]):
        return "Hello! How can I help?"
    else:
        return ask_gemini(api_key, command)

def main():
    API_KEY = 'AIzaSyCr5FxRDDxc7-evSfrAlGZwBukegoznYUg'
    voice_mode = True  # Start with voice input by default
    
    print("=" * 70)
    print("🎤 VOICE ASSISTANT - VIOLET (Gemini)")
    print("=" * 70)
    print("\n📋 Commands: time, date, weather, news, open [app], search [query], exit")
    print("💡 Type 'voice' to toggle voice mode, 'text' for text mode\n")
    
    speak("Voice assistant activated. I'm listening. Say something!")
    
    while True:
        try:
            if voice_mode:
                # Voice input mode
                user_input = listen()
                if user_input is None:
                    continue
            else:
                # Text input mode
                user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Toggle mode commands
            if user_input.lower() in ["voice", "voice mode", "switch to voice"]:
                voice_mode = True
                speak("Voice mode activated. I'm listening!")
                continue
            elif user_input.lower() in ["text", "text mode", "switch to text", "type"]:
                voice_mode = False
                speak("Text mode activated. Type your message.")
                continue
            
            if any(w in user_input.lower() for w in ["exit", "quit", "bye", "stop"]):
                speak("Goodbye!")
                break
            
            response = process_command(user_input, API_KEY)
            speak(response)
            
        except KeyboardInterrupt:
            speak("Shutting down")
            break
        except Exception as e:
            print(f"Error: {e}")
            if voice_mode:
                print("💡 Switching to text mode due to error...")
                voice_mode = False

if __name__ == "__main__":
    main()