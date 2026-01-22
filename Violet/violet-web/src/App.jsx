import React, { useState, useEffect, useRef, useCallback } from 'react'
import { processLocalCommand } from './utils/brain'
import { Login3D } from './components/Login3D'
import { VoiceAssistant } from './components/VoiceAssistant'
import './App.css'

// ================================================
// Main App Component (Controller)
// ================================================

function App() {
  const [messages, setMessages] = useState([])
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isMuted, setIsMuted] = useState(false)

  // Settings State
  const [settings, setSettings] = useState(() => {
    // Initial load from localStorage
    const saved = localStorage.getItem('violet_settings');
    if (saved) {
      return JSON.parse(saved);
    }
    return {
      voiceEnabled: true,
      autoSend: false,
      soundEffects: true,
      theme: 'dark',
      language: 'en',
      voiceSpeed: 'normal',
      notifications: true,
    };
  });

  const updateSettings = (key, value) => {
    console.log(`[App] updateSettings called: key=${key}, value=${value}`);
    setSettings(prev => {
      const newSettings = { ...prev, [key]: value };
      console.log('[App] New settings:', newSettings);
      localStorage.setItem('violet_settings', JSON.stringify(newSettings));
      return newSettings;
    });
  };
  // Keep settings specific ref for callbacks
  const settingsRef = useRef(settings)
  useEffect(() => {
    settingsRef.current = settings;
    // Update lang dynamically if recognition exists
    if (recognitionRef.current) {
      recognitionRef.current.lang = settings.language === 'en' ? 'en-US' :
        settings.language === 'es' ? 'es-ES' :
          settings.language === 'fr' ? 'fr-FR' :
            settings.language === 'de' ? 'de-DE' : 'en-US';
    }
  }, [settings])

  // Input State
  const [inputText, setInputText] = useState("")

  const recognitionRef = useRef(null)
  const synthRef = useRef(window.speechSynthesis)

  // Authentication State
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  // Apply Theme
  useEffect(() => {
    console.log('[App] Theme effect running. Current theme:', settings.theme);
    const root = document.documentElement;
    const applyTheme = (theme) => {
      console.log('[App] Applying theme:', theme);
      if (theme === 'system') {
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        root.classList.toggle('dark', systemDark);
        root.classList.toggle('light', !systemDark);
      } else {
        root.classList.toggle('dark', theme === 'dark');
        root.classList.toggle('light', theme === 'light');
      }
      console.log('[App] document.documentElement classes:', root.className);
    };
    applyTheme(settings.theme);
  }, [settings.theme]);

  // Speak text with female voice
  const speak = useCallback((text) => {
    if (!synthRef.current || isMuted) return

    if (synthRef.current.speaking) {
      synthRef.current.cancel()
    }

    const speechText = text.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F900}-\u{1F9FF}\u{1F000}-\u{1F2FF}\u{2300}-\u{23FF}\u{2B50}\u{2500}-\u{257F}]/gu, '')
      .replace(/\*/g, '')
      .replace(/[|:-]/g, ' ')

    const utterance = new SpeechSynthesisUtterance(speechText)
    const voices = synthRef.current.getVoices()

    const femaleVoice = voices.find(voice =>
      voice.name.includes('Zira') ||
      voice.name.includes('Female') ||
      voice.name.includes('Samantha') ||
      voice.name.includes('Google UK English Female')
    ) || voices.find(voice => voice.lang.includes('en'))

    if (femaleVoice) utterance.voice = femaleVoice

    // Apply speed setting
    const speedMap = { slow: 0.8, normal: 1.0, fast: 1.2 };
    utterance.rate = speedMap[settings.voiceSpeed] || 1.0;
    utterance.pitch = 1.1

    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => {
      setIsSpeaking(false)
    }

    synthRef.current.speak(utterance)
  }, [isMuted, settings.voiceSpeed])

  const handleLogin = (isVoice) => {
    setIsLoggedIn(true)
    const method = isVoice ? "Voice verified" : "Password verified"
    speak(`Welcome back, Thamim. ${method}. Systems online.`)
  }

  // Check backend connection
  useEffect(() => {
    const checkConnection = () => {
      const protocol = window.location.protocol
      const hostname = window.location.hostname
      fetch(`${protocol}//${hostname}:8000/health`)
        .then(res => res.json())
        .then(() => setIsConnected(true))
        .catch(() => setIsConnected(false))
    }

    checkConnection()
    const interval = setInterval(checkConnection, 10000)
    return () => clearInterval(interval)
  }, [])

  // Send message to backend
  const handleSendMessage = async (text) => {
    if (!text.trim() || isLoading) return

    // Clear input if strictly sending
    setInputText("")

    const userMessage = { role: 'user', content: text, timestamp: new Date() }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    // Check Local Brain First
    const localResponse = processLocalCommand(text)
    if (localResponse) {
      setTimeout(() => {
        const assistantMessage = { role: 'assistant', content: localResponse, timestamp: new Date() }
        setMessages(prev => [...prev, assistantMessage])
        speak(localResponse)
        setIsLoading(false)
      }, 300)
      return
    }

    try {
      const protocol = window.location.protocol
      const hostname = window.location.hostname
      const backendUrl = `${protocol}//${hostname}:8001/chat`

      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      })

      const data = await response.json()
      const assistantMessage = { role: 'assistant', content: data.response, timestamp: new Date() }
      setMessages(prev => [...prev, assistantMessage])
      speak(data.response)
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Connection Error to ${backendUrl}: ${error.message}. Cause: ${error.cause ? error.cause : 'Unknown'}. Check console for details.`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // WebSocket for real-time events (Clap)
  useEffect(() => {
    let ws;
    try {
      ws = new WebSocket('ws://localhost:8001/ws');

      ws.onmessage = (event) => {
        if (event.data === "clap_detected") {
          const newMessage = {
            role: "assistant",
            content: "👏 Clap command detected! Playing Sao Paulo..."
          };
          setMessages(prev => [...prev, newMessage]);
        }
      };

      ws.onopen = () => { console.log('[App] WebSocket Connected'); };
      ws.onclose = () => { console.log('[App] WebSocket Disconnected'); };
    } catch (error) {
      console.error("WebSocket Error:", error);
    }

    return () => {
      if (ws) ws.close();
    };
  }, []);
  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      // Only create if not exists
      if (!recognitionRef.current) {
        recognitionRef.current = new SpeechRecognition()
        recognitionRef.current.continuous = false
        recognitionRef.current.interimResults = false
      }

      // Update lang from ref immediately
      const currentSettings = settingsRef.current;
      recognitionRef.current.lang = currentSettings.language === 'en' ? 'en-US' :
        currentSettings.language === 'es' ? 'es-ES' :
          currentSettings.language === 'fr' ? 'fr-FR' :
            currentSettings.language === 'de' ? 'de-DE' : 'en-US';

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        // Use ref to get latest setting without re-binding
        if (settingsRef.current.autoSend) {
          handleSendMessage(transcript)
        } else {
          setInputText(transcript)
        }
      }

      recognitionRef.current.onerror = () => {
        setIsListening(false)
      }

      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    }
  }, []) // Empty dependency array - run once

  const toggleListening = useCallback(() => {
    if (!recognitionRef.current || isLoading) return
    if (!settings.voiceEnabled) {
      // Maybe notify user?
      return;
    }

    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    } else {
      try {
        recognitionRef.current.start()
        setIsListening(true)
      } catch (err) {
        console.error("Speech recognition start error:", err)
        setIsListening(false)
      }
    }
  }, [isListening, isLoading, settings.voiceEnabled])

  const toggleMute = () => {
    setIsMuted(prev => !prev)
    if (!isMuted) {
      if (synthRef.current) synthRef.current.cancel()
      setIsSpeaking(false)
    }
  }

  return (
    <div className="app">
      {!isLoggedIn ? (
        <Login3D onLogin={handleLogin} />
      ) : (
        <VoiceAssistant
          messages={messages}
          isListening={isListening}
          isSpeaking={isSpeaking}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
          onToggleListening={toggleListening}
          isMuted={isMuted}
          onToggleMute={toggleMute}
          settings={settings}
          onUpdateSettings={updateSettings}
          inputText={inputText}
          setInputText={setInputText}
        />
      )}
    </div>
  )
}

export default App
