import pyttsx3
import subprocess
from datetime import datetime
import requests
import webbrowser
import platform

engine = pyttsx3.init()

def speak(text):
    """Convert text to speech"""
    try:
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        print(f"🤖 Assistant: {text}")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error speaking: {e}")
        print(f"🤖 Assistant: {text}")

def listen():
    """Listen to user voice input using Windows built-in speech recognition"""
    try:
        import winsound
        print("🎤 Listening...")
        
        # Use Windows PowerShell for speech recognition
        ps_command = """
        Add-Type -AssemblyName System.Speech
        $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
        $recognizer.SetInputToDefaultAudioDevice()
        $result = $recognizer.Recognize()
        if ($result) { Write-Host $result.Text } else { Write-Host "null" }
        """
        
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        text = result.stdout.strip()
        if text and text.lower() != "null":
            print(f"👤 You said: {text}")
            return text.lower()
        else:
            print("Could not understand audio")
            return None
    except subprocess.TimeoutExpired:
        print("Listening timeout")
        return None
    except Exception as e:
        print(f"Listening error: {e}")
        return None

def get_time():
    """Get current time"""
    return datetime.now().strftime("%H:%M:%S")

def get_date():
    """Get current date"""
    return datetime.now().strftime("%A, %B %d, %Y")

def get_weather(city="New York"):
    """Get weather information"""
    try:
        url = f"https://wttr.in/{city}?format=3"
        response = requests.get(url, timeout=5)
        return response.text if response.status_code == 200 else "Could not fetch weather"
    except:
        return "Unable to get weather information"

def open_app(app_name):
    """Open applications based on name"""
    app_name = app_name.lower().strip()
    
    if platform.system() == "Windows":
        # Specific paths for common apps
        app_paths = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
            "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "terminal": "wt.exe",
            "powershell": "powershell.exe",
            "vscode": r"C:\Users\lenova\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            "spotify": r"C:\Users\lenova\AppData\Roaming\Spotify\Spotify.exe"
        }

        # Special handling for YouTube (User requested specific path)
        if app_name in ["youtube", "yt"]:
            try:
                chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                subprocess.Popen([chrome_path, "--app=https://www.youtube.com"])
                return "Opening YouTube"
            except Exception as e:
                return f"Could not open YouTube: {e}"
        
        if app_name in app_paths:
            try:
                subprocess.Popen(app_paths[app_name])
                return f"Opening {app_name}"
            except Exception as e:
                return f"Could not open {app_name}: {e}"

        # Fallback: Try to open via system command
        try:
            subprocess.Popen(["start", app_name], shell=True)
            return f"Attempting to open {app_name}"
        except:
            pass
    
    elif platform.system() == "Darwin":  # macOS
        app_names = {
            "chrome": "Google Chrome",
            "safari": "Safari",
            "notepad": "TextEdit",
            "calculator": "Calculator",
            "finder": "Finder",
            "word": "Microsoft Word",
            "excel": "Microsoft Excel"
        }
        
        if app_name in app_names:
            try:
                subprocess.Popen(["open", "-a", app_names[app_name]])
                return f"Opening {app_name}"
            except:
                return f"Could not open {app_name}"
                
        # Fallback
        try:
            subprocess.Popen(["open", "-a", app_name])
            return f"Attempting to open {app_name}"
        except:
            pass
    
    elif platform.system() == "Linux":
        linux_apps = {
            "chrome": "google-chrome",
            "firefox": "firefox",
            "notepad": "gedit",
            "calculator": "gnome-calculator"
        }
        
        if app_name in linux_apps:
            try:
                subprocess.Popen([linux_apps[app_name]])
                return f"Opening {app_name}"
            except:
                return f"Could not open {app_name}"

    return f"Application {app_name} not found"

def search_web(query):
    """Open web search in browser"""
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching for {query}"
