import os
from dotenv import load_dotenv

load_dotenv()

# Replace with your own Gemini API key from https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyC1r4Cab7A6qpMyMDeDP8XjzCISObS01Vs')
GNEWS_API_KEY = os.getenv('GNEWS_API_KEY', 'your_gnews_api_key_here')  # Get free key from https://gnews.io/
VOICE_RATE = 150
VOICE_VOLUME = 1.0