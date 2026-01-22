import { useState, useEffect, useRef } from 'react'
import '../App.css'

export default function Login({ onLogin }) {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [isListening, setIsListening] = useState(false)
    const recognitionRef = useRef(null)

    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
            recognitionRef.current = new SpeechRecognition()
            recognitionRef.current.continuous = false
            recognitionRef.current.interimResults = false
            recognitionRef.current.lang = 'en-US'

            recognitionRef.current.onresult = (event) => {
                const transcript = event.results[0][0].transcript.toLowerCase()
                console.log("Voice Auth Heard:", transcript)

                // Simple Passphrase "Voice Match" Logic
                if (transcript.includes("authenticate") || transcript.includes("login") || transcript.includes("verify me") || transcript.includes("access")) {
                    onLogin(true) // Voice Login Success
                } else {
                    setError("Voice not matched. Please try again.")
                    setTimeout(() => setError(''), 3000)
                }
                setIsListening(false)
            }

            recognitionRef.current.onerror = (e) => {
                console.error("Voice Auth Error:", e)
                setError("Voice detection failed.")
                setIsListening(false)
            }

            recognitionRef.current.onend = () => {
                setIsListening(false)
            }
        }
    }, [onLogin])

    const handleTextLogin = (e) => {
        e.preventDefault()
        if (username.toLowerCase() === 'thamim' && password === 'thamim') {
            onLogin(false) // Text Login Success
        } else {
            setError("Invalid Username or Password")
        }
    }

    const startVoiceAuth = () => {
        setError('')
        if (recognitionRef.current && !isListening) {
            try {
                setIsListening(true)
                recognitionRef.current.start()
            } catch (e) {
                console.error(e)
                setIsListening(false)
            }
        }
    }

    return (
        <div className="login-container">
            <div className="login-box glass-panel">
                <div className="login-header">
                    <div className="logo-icon large">V</div>
                    <h1>Welcome Back</h1>
                    <p>Sign in to VIOLET</p>
                </div>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleTextLogin}>
                    <div className="input-group">
                        <input
                            type="text"
                            placeholder="Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>
                    <div className="input-group">
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="login-btn">
                        Login
                    </button>
                </form>

                <div className="divider">
                    <span>OR</span>
                </div>

                <button
                    className={`voice-auth-btn ${isListening ? 'listening' : ''}`}
                    onClick={startVoiceAuth}
                    disabled={isListening}
                >
                    <div className="voice-wave">
                        {isListening ? (
                            <>
                                <span></span><span></span><span></span><span></span><span></span>
                            </>
                        ) : "🎤"}
                    </div>
                    {isListening ? "Listening..." : "Authenticate with Voice"}
                </button>

                {isListening && <p className="voice-instruction">Say "Authenticate", "Login", or "Verify Me"</p>}
            </div>
        </div>
    )
}
