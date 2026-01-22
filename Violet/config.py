import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDX8WDT_mcqGPh1qHYZf5qXB0YMd5IT8u8')
GNEWS_API_KEY = os.getenv('GNEWS_API_KEY', 'your_gnews_api_key_here')  # Get free key from https://gnews.io/
VOICE_RATE = 150
VOICE_VOLUME = 1.0