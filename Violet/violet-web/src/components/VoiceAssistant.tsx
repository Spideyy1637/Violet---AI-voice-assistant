"use client";

import { useState, useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import { Mic, Send, Settings, Bot } from "lucide-react";
import SettingsPanel from "./ui/SettingsPanel";
import { VoicePoweredOrb } from "@/components/ui/voice-powered-orb";
import EnergyBeam from "@/components/ui/energy-beam";
import { AuroraText } from "@/components/ui/aurora-text";

interface Message {
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
}

interface VoiceAssistantProps {
    messages: Message[];
    isListening: boolean;
    isSpeaking: boolean;
    isLoading: boolean;
    onSendMessage: (text: string) => void;
    onToggleListening: () => void;
    isMuted: boolean;
    onToggleMute: () => void;
    settings: any;
    onUpdateSettings: (key: string, value: any) => void;
    inputText: string;
    setInputText: (text: string) => void;
}

export function VoiceAssistant({
    messages,
    isListening,
    isSpeaking,
    isLoading,
    onSendMessage,
    onToggleListening,
    settings,
    onUpdateSettings,
    inputText,
    setInputText
}: VoiceAssistantProps) {
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSend = () => {
        if (inputText.trim()) {
            onSendMessage(inputText.trim());
            // Input clearing is handled by parent if needed, 
            // but for safety we can't clear it here if onSendMessage is async/parent handled?
            // Actually parent clears it in handleSendMessage.
            if (textareaRef.current) textareaRef.current.style.height = "auto";
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInputText(e.target.value);
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
        }
    };

    const formatTime = (date: Date) => {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="chat-app relative overflow-hidden z-0">
            {/* Background */}
            <EnergyBeam className="absolute inset-0 -z-10 pointer-events-none" />

            {/* Header */}
            <header className="chat-header-bar">
                <div className="header-left">
                    <div className="relative cursor-pointer" onClick={onToggleListening}>
                        {messages.length > 0 ? (
                            <div className="h-10 w-10">
                                <VoicePoweredOrb
                                    mode={isListening ? "listening" : "idle"}
                                    hue={280}
                                    onVoiceDetected={() => { }}
                                />
                            </div>
                        ) : (
                            <div className="app-icon">
                                <Bot size={20} />
                            </div>
                        )}
                    </div>
                    <span className="app-name">
                        <AuroraText>Violet</AuroraText> AI
                    </span>
                </div>
                <button
                    className="settings-btn"
                    aria-label="Settings"
                    onClick={() => setIsSettingsOpen(true)}
                >
                    <Settings size={20} />
                </button>
            </header>

            {/* Chat Area */}
            <main className="chat-messages-area">
                {messages.length === 0 ? (
                    <div className="empty-state">
                        <div className="mb-8 text-center">
                            <h2>How can I help you today?</h2>
                            <p>Send a message or tap the microphone to speak</p>
                        </div>

                        {/* Dynamic Orb */}
                        <div className="relative cursor-pointer group pointer-events-auto h-64 w-64 flex items-center justify-center mb-8" onClick={onToggleListening}>
                            <VoicePoweredOrb
                                mode={isListening ? "listening" : "idle"}
                                hue={280} // Violet/Purple
                                onVoiceDetected={() => { }}
                            />
                        </div>

                        <div className="suggestion-chips">
                            {["Explain something", "Help me write", "Answer a question", "Just chat"].map((prompt, i) => (
                                <button
                                    key={i}
                                    onClick={() => onSendMessage(prompt)}
                                    className="suggestion-chip"
                                >
                                    {prompt}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="messages-list">
                        {messages.map((msg, i) => (
                            <div
                                key={i}
                                className={cn(
                                    "message-row",
                                    msg.role === "user" ? "user-message" : "assistant-message"
                                )}
                            >
                                {msg.role === "assistant" && (
                                    <div className="message-avatar">
                                        <Bot size={16} />
                                    </div>
                                )}
                                <div className="message-content">
                                    <div className={cn(
                                        "message-bubble",
                                        msg.role === "user" ? "user-bubble" : "assistant-bubble"
                                    )}>
                                        {msg.content}
                                    </div>
                                    <span className="message-time">{formatTime(msg.timestamp)}</span>
                                </div>
                            </div>
                        ))
                        }

                        {/* Loading indicator */}
                        {isLoading && (
                            <div className="message-row assistant-message">
                                <div className="message-avatar">
                                    <Bot size={16} />
                                </div>
                                <div className="message-content">
                                    <div className="message-bubble assistant-bubble typing-bubble">
                                        <div className="typing-dots">
                                            <span></span>
                                            <span></span>
                                            <span></span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )
                }
                <div ref={messagesEndRef} />
            </main>

            {/* Input Bar */}
            <footer className="chat-input-bar">
                <div className="input-container">
                    <button
                        onClick={onToggleListening}
                        className={cn(
                            "mic-btn",
                            isListening && "mic-active"
                        )}
                        aria-label={isListening ? "Stop listening" : "Start voice input"}
                    >
                        <Mic size={20} />
                        {isListening && <span className="mic-pulse"></span>}
                    </button>

                    <textarea
                        ref={textareaRef}
                        value={inputText}
                        onChange={handleInputChange}
                        onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey) {
                                e.preventDefault();
                                handleSend();
                            }
                        }}
                        placeholder="Message Violet AI..."
                        rows={1}
                        className="message-input"
                    />

                    <button
                        onClick={handleSend}
                        disabled={!inputText.trim()}
                        className={cn(
                            "send-btn",
                            inputText.trim() && "send-active"
                        )}
                        aria-label="Send message"
                    >
                        <Send size={18} />
                    </button>
                </div>
            </footer >

            {/* Settings Panel */}
            < SettingsPanel
                isOpen={isSettingsOpen}
                onClose={() => setIsSettingsOpen(false)}
                settings={settings}
                onUpdateSettings={onUpdateSettings}
            />

            < style > {`
                /* ========================================
                   Professional Chat UI - Production Ready
                   ======================================== */
                /* Chat App Container */
                .chat-app {
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                    width: 100%;
                    background: transparent;
                    color: var(--text-primary);
                    font-family: var(--font-body);
                }

                /* Header Bar */
                .chat-header-bar {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 0 20px;
                    height: 56px;
                    background: transparent;
                    border-bottom: none;
                    flex-shrink: 0;
                }

                .header-left {
                    display: flex;
                    align-items: center;
                    gap: 24px;
                }

                .app-icon {
                    width: 32px;
                    height: 32px;
                    background: var(--neon-blue);
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                }

                .app-name {
                    font-size: 24px;
                    font-weight: 700;
                    letter-spacing: -0.02em;
                    color: var(--text-primary);
                }

                .settings-btn {
                    width: 36px;
                    height: 36px;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: var(--text-muted);
                    background: transparent;
                    border: none;
                    cursor: pointer;
                    transition: all 0.15s ease;
                }

                .settings-btn:hover {
                    background: var(--bg-surface);
                    color: var(--text-primary);
                }

                /* Chat Messages Area */
                .chat-messages-area {
                    flex: 1;
                    overflow-y: auto;
                    padding: 24px 16px;
                    display: flex;
                    flex-direction: column;
                }

                .chat-messages-area::-webkit-scrollbar {
                    width: 6px;
                }

                .chat-messages-area::-webkit-scrollbar-track {
                    background: transparent;
                }

                .chat-messages-area::-webkit-scrollbar-thumb {
                    background: var(--glass-border);
                    border-radius: 3px;
                }

                .chat-messages-area::-webkit-scrollbar-thumb:hover {
                    background: var(--text-muted);
                }

                /* Empty State */
                .empty-state {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    flex: 1;
                    text-align: center;
                    padding: 20px;
                }

                .empty-icon {
                    display: none;
                }

                .empty-state h2 {
                    font-size: 24px;
                    font-weight: 600;
                    margin-bottom: 8px;
                    color: var(--text-primary);
                }

                .empty-state p {
                    font-size: 15px;
                    color: var(--text-muted);
                    margin-bottom: 32px;
                }

                .suggestion-chips {
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    gap: 8px;
                    max-width: 400px;
                }

                .suggestion-chip {
                    padding: 10px 16px;
                    background: var(--bg-surface);
                    border: 1px solid var(--glass-border);
                    border-radius: 20px;
                    color: var(--text-secondary);
                    font-size: 14px;
                    cursor: pointer;
                    transition: all 0.15s ease;
                }

                .suggestion-chip:hover {
                    background: var(--bg-deep);
                    color: var(--text-primary);
                    border-color: var(--text-muted);
                }

                /* Messages List */
                .messages-list {
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                    max-width: 768px;
                    width: 100%;
                    margin: 0 auto;
                }

                /* Message Row */
                .message-row {
                    display: flex;
                    gap: 12px;
                    animation: messageIn 0.2s ease-out;
                }

                @keyframes messageIn {
                    from {
                        opacity: 0;
                        transform: translateY(8px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                .user-message {
                    justify-content: flex-end;
                }

                .assistant-message {
                    justify-content: flex-start;
                }

                .message-avatar {
                    width: 28px;
                    height: 28px;
                    background: var(--bg-surface);
                    border-radius: 6px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: var(--text-muted);
                    flex-shrink: 0;
                    margin-top: 2px;
                }

                .message-content {
                    max-width: 70%;
                    display: flex;
                    flex-direction: column;
                }

                .user-message .message-content {
                    align-items: flex-end;
                }

                .assistant-message .message-content {
                    align-items: flex-start;
                }

                /* Message Bubbles */
                .message-bubble {
                    padding: 12px 16px;
                    border-radius: 18px;
                    font-size: 15px;
                    line-height: 1.5;
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                }

                .user-bubble {
                    background: var(--neon-blue);
                    color: #ffffff;
                    border-bottom-right-radius: 4px;
                }

                .assistant-bubble {
                    background: var(--bg-surface);
                    color: var(--text-primary);
                    border-bottom-left-radius: 4px;
                    border: 1px solid var(--glass-border);
                }

                .message-time {
                    font-size: 11px;
                    color: var(--text-muted);
                    margin-top: 4px;
                    padding: 0 4px;
                }

                /* Typing Indicator */
                .typing-bubble {
                    padding: 16px 20px;
                }

                .typing-dots {
                    display: flex;
                    gap: 4px;
                }

                .typing-dots span {
                    width: 8px;
                    height: 8px;
                    background: var(--text-muted);
                    border-radius: 50%;
                    animation: typingBounce 1.4s infinite ease-in-out;
                }

                .typing-dots span:nth-child(1) {
                    animation-delay: 0s;
                }

                .typing-dots span:nth-child(2) {
                    animation-delay: 0.2s;
                }

                .typing-dots span:nth-child(3) {
                    animation-delay: 0.4s;
                }

                @keyframes typingBounce {
                    0%, 60%, 100% {
                        transform: translateY(0);
                    }
                    30% {
                        transform: translateY(-4px);
                    }
                }

                /* Input Bar */
                .chat-input-bar {
                    padding: 16px;
                    background: transparent;
                    border-top: none;
                    flex-shrink: 0;
                }

                .input-container {
                    display: flex;
                    align-items: flex-end;
                    gap: 8px;
                    max-width: 768px;
                    margin: 0 auto;
                    background: var(--bg-deep);
                    border: 1px solid var(--glass-border);
                    border-radius: 24px;
                    padding: 8px 8px 8px 4px;
                    transition: border-color 0.15s ease;
                }

                .input-container:focus-within {
                    border-color: var(--neon-blue);
                }

                /* Mic Button */
                .mic-btn {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: transparent;
                    border: none;
                    color: var(--text-muted);
                    cursor: pointer;
                    transition: all 0.15s ease;
                    position: relative;
                    flex-shrink: 0;
                }

                .mic-btn:hover {
                    color: var(--text-primary);
                    background: var(--bg-surface);
                }

                .mic-btn.mic-active {
                    color: #ffffff;
                    background: #ef4444;
                }

                .mic-pulse {
                    position: absolute;
                    inset: 0;
                    border-radius: 50%;
                    background: #ef4444;
                    animation: micPulse 1.5s infinite;
                    z-index: -1;
                }

                @keyframes micPulse {
                    0% {
                        transform: scale(1);
                        opacity: 0.6;
                    }
                    100% {
                        transform: scale(1.8);
                        opacity: 0;
                    }
                }

                /* Message Input */
                .message-input {
                    flex: 1;
                    background: transparent;
                    border: none;
                    outline: none;
                    color: var(--text-primary);
                    font-size: 15px;
                    line-height: 1.5;
                    padding: 8px 0;
                    resize: none;
                    max-height: 120px;
                    font-family: inherit;
                }

                .message-input::placeholder {
                    color: var(--text-muted);
                }

                /* Send Button */
                .send-btn {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: var(--bg-surface);
                    border: none;
                    color: var(--text-muted);
                    cursor: not-allowed;
                    transition: all 0.15s ease;
                    flex-shrink: 0;
                }

                .send-btn.send-active {
                    background: var(--neon-blue);
                    color: #ffffff;
                    cursor: pointer;
                }

                .send-btn.send-active:hover {
                    opacity: 0.9;
                }

                /* Mobile Responsiveness */
                @media (max-width: 640px) {
                    .chat-header-bar {
                        padding: 0 16px;
                    }

                    .chat-messages-area {
                        padding: 16px 12px;
                    }

                    .message-content {
                        max-width: 85%;
                    }

                    .empty-state h2 {
                        font-size: 20px;
                    }

                    .suggestion-chips {
                        gap: 6px;
                    }

                    .suggestion-chip {
                        padding: 8px 14px;
                        font-size: 13px;
                    }

                    .chat-input-bar {
                        padding: 12px;
                    }

                    .input-container {
                        padding: 6px 6px 6px 2px;
                    }

                    .mic-btn,
                    .send-btn {
                        width: 36px;
                        height: 36px;
                    }

                    .message-input {
                        font-size: 16px; /* Prevents zoom on iOS */
                    }
                }
            `}</style >
        </div >
    );
}
