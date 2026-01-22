from utils import speak, listen, get_time, get_date, get_weather, open_app, search_web

class CommandHandler:
    def __init__(self, openai_client):
        self.client = openai_client
    
    def handle_command(self, command):
        """Route commands to appropriate handlers"""
        command = command.lower().strip()
        
        if any(word in command for word in ["time", "what time"]):
            return f"The time is {get_time()}"
        
        elif any(word in command for word in ["date", "what day", "today"]):
            return f"Today is {get_date()}"
        
        elif any(word in command for word in ["weather", "temperature"]):
            city = self.extract_city(command)
            return get_weather(city)
        
        elif any(word in command for word in ["open", "launch"]):
            app = self.extract_app(command)
            return open_app(app)
        
        elif any(word in command for word in ["search", "find", "look up"]):
            query = command.replace("search", "").replace("find", "").replace("look up", "").strip()
            return search_web(query)
        
        elif any(word in command for word in ["hello", "hi", "hey"]):
            return "Hello! How can I help you today?"
        
        elif any(word in command for word in ["quit", "exit", "stop"]):
            return "goodbye"
        
        else:
            return self.ask_openai(command)
    
    def extract_app(self, command):
        """Extract app name from command"""
        apps = ["chrome", "firefox", "notepad", "calculator", "word", "excel", "safari", "edge", "paint"]
        for app in apps:
            if app in command:
                return app
        return command.replace("open", "").replace("launch", "").strip()
    
    def extract_city(self, command):
        """Extract city name from weather command"""
        words = command.split()
        if len(words) > 1:
            return " ".join(words[-2:])
        return "New York"
    
    def ask_openai(self, question):
        """Send query to OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful voice assistant. Keep responses concise (max 2-3 sentences) for voice output."},
                    {"role": "user", "content": question}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"