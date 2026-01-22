from openai import OpenAI
from handlers import CommandHandler
from utils import speak, listen
import sys

class VoiceAssistant:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.handler = CommandHandler(self.client)
        self.running = False
    
    def start(self):
        """Start the voice assistant"""
        self.running = True
        speak("Voice assistant activated. How can I help?")
        
        while self.running:
            try:
                command = listen()
                
                if command is None:
                    continue
                
                response = self.handler.handle_command(command)
                
                if response == "goodbye":
                    speak("Goodbye!")
                    self.running = False
                else:
                    speak(response)
            
            except KeyboardInterrupt:
                speak("Shutting down")
                self.running = False
            except Exception as e:
                print(f"Error: {e}")
                speak("An error occurred")