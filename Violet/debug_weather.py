import requests

def debug_weather(city="chennai"):
    print(f"Testing City: '{city}'")
    url = f"https://wttr.in/{city}?format=3"
    print(f"URL: {url}")
    try:
        # Mimic strict timeout from server code
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        print(f"Headers: {response.headers}")
    except Exception as e:
        print(f"Exception: {e}")

debug_weather("chennai")
debug_weather("New York")
