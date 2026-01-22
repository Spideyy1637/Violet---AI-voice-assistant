'use client'

import { SplineScene } from "@/components/ui/splite";
import { Card } from "@/components/ui/card"
import { Spotlight } from "@/components/ui/spotlight"
import React, { useState } from "react"
import ShaderBackground from "@/components/ui/shader-background"
import { VoicePoweredOrb } from "@/components/ui/voice-powered-orb"

interface Login3DProps {
    onLogin: (isVoice: boolean) => void;
}

export function Login3D({ onLogin }: Login3DProps) {
    const [orbState, setOrbState] = useState<"idle" | "listening" | "authorized" | "error">("idle");
    const [transcript, setTranscript] = useState("");
    const splineAppRef = React.useRef<any>(null);

    const onSplineLoad = (spline: any) => {
        splineAppRef.current = spline;
        console.log("Spline loaded", spline);
    };

    const triggerSplineEvent = (eventName: string) => {
        if (splineAppRef.current) {
            try {
                splineAppRef.current.emitEvent(eventName);
                // Also try setting variables if events aren't mapped
                if (eventName === 'listening') splineAppRef.current.setVariable('State', 1);
                if (eventName === 'success') splineAppRef.current.setVariable('State', 2);
                if (eventName === 'fail') splineAppRef.current.setVariable('State', 3);
            } catch (e) {
                console.warn("Error triggering spline event:", e);
            }
        }
    };

    const playSuccessSound = () => {
        // Placeholder for success sound - using a simple oscillator for now or just visual
        // In a real app, use: new Audio('/sounds/success.mp3').play();
        const AudioContext = (window as any).AudioContext || (window as any).webkitAudioContext;
        if (AudioContext) {
            const ctx = new AudioContext();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(440, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.5);
            gain.gain.setValueAtTime(0.1, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.5);
        }
    };

    const handleVoiceAuth = () => {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

        if (!SpeechRecognition) {
            alert("Voice authentication is not supported in this browser.");
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        recognition.interimResults = true; // Changed to true for real-time feedback

        setOrbState("listening");
        setTranscript("Listening...");
        triggerSplineEvent('listening');

        recognition.onresult = (event: any) => {
            const current = event.resultIndex;
            const transcriptText = event.results[current][0].transcript.toLowerCase();
            setTranscript(transcriptText);

            if (event.results[current].isFinal) {
                if (transcriptText.includes("log") || transcriptText.includes("login") || transcriptText.includes("enter") || transcriptText.includes("violet") || transcriptText.includes("open")) {
                    setOrbState("authorized");
                    setTranscript("Access Granted");
                    triggerSplineEvent('success');
                    playSuccessSound();
                    setTimeout(() => {
                        onLogin(true);
                    }, 2000);
                } else {
                    setOrbState("error");
                    setTranscript("Access Denied");
                    triggerSplineEvent('fail');
                    setTimeout(() => {
                        setOrbState("idle");
                        setTranscript("");
                    }, 2000);
                }
            }
        };

        recognition.onerror = (event: any) => {
            console.error("Speech recognition error", event.error);
            setOrbState("error");
            setTranscript("Error. Try again.");
            triggerSplineEvent('fail');
            setTimeout(() => {
                setOrbState("idle");
                setTranscript("");
            }, 2000);
        };

        recognition.onend = () => {
            if (orbState === "listening") { // Only reset if not authorized or already error handled
                // Keep listening state briefly or reset? 
                // If silence, maybe reset.
                if (transcript === "Listening...") {
                    setOrbState("idle");
                    setTranscript("");
                }
            }
        };

        try {
            recognition.start();
        } catch (err) {
            console.error(err);
            setOrbState("idle");
        }
    }

    return (
        <Card className="w-full h-screen bg-black relative overflow-hidden border-none rounded-none m-0 p-0 flex items-center justify-center">
            <Spotlight
                className="-top-40 left-0 md:left-60 md:-top-20"
                fill="#ff1f1f"
            />

            {/* Spline Scene - Background */}
            <div className="absolute inset-0 z-0 w-full h-full">
                {/* Shader Background - Deepest Layer */}
                <div className="absolute inset-0 -z-20">
                    <ShaderBackground />
                </div>

                <SplineScene
                    scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
                    className="w-full h-full"
                    onLoad={onSplineLoad}
                />
                {/* Reduced opacity of gradient to make robot more visible */}
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent z-10 pointer-events-none" />
            </div>

            {/* Skip Button - Top Right */}
            <button
                onClick={() => onLogin(false)}
                className="absolute top-6 right-6 z-30 px-4 py-2 text-sm font-medium text-gray-300 hover:text-white bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 rounded-lg transition-all duration-300 hover:scale-105"
            >
                Skip →
            </button>

            {/* Foreground Content - pointer-events-none allows clicks to pass through to 3D scene in empty areas */}
            <div className="relative z-20 flex flex-col items-center justify-center w-full h-full pointer-events-none">



                {/* Violet Orb - Voice Powered with OGL */}
                <div className="relative cursor-pointer group pointer-events-auto h-48 w-48 md:h-64 md:w-64" onClick={handleVoiceAuth}>
                    {/* 
                        Mapping visual states: 
                        - Listening: enableVoiceControl = true
                        - Authorized: hue shift to Green (done via prop or better yet, simple handling)
                        - we can pass different hues based on state.
                        Default green hue ~ 120. Cyan ~ 180. Purple ~ 280.
                     */}
                    <VoicePoweredOrb
                        enableVoiceControl={orbState === 'listening'}
                        hue={orbState === 'authorized' ? 120 : orbState === 'error' ? 0 : 280} // 120 Green, 0 Red, 280 Purple
                        onVoiceDetected={(detected) => {
                            // Optional: could trigger visual feedback elsewhere
                        }}
                    />
                </div>

                {/* Status Text */}
                <div className="mt-16 h-8 flex flex-col items-center">
                    <p className={`text-lg font-[Inter] tracking-wide transition-all duration-300 min-h-[1.5rem]
                        ${orbState === 'idle' && 'text-gray-400'}
                        ${orbState === 'listening' && 'text-violet-300 font-semibold animate-pulse'}
                        ${orbState === 'authorized' && 'text-green-400 font-bold'}
                        ${orbState === 'error' && 'text-red-400'}
                    `}>
                        {transcript || "Tap Orb to Authenticate"}
                    </p>
                    {orbState === 'idle' && (
                        <p className="text-xs text-gray-600 mt-2">Say "Violet" or "Login"</p>
                    )}
                </div>
            </div>
        </Card>
    )
}
