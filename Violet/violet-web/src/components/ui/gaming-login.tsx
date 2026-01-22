'use client';
import React, { useState } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion';
import { Mail, Lock, Eye, EyeOff, ArrowRight, Mic, User } from 'lucide-react';
import { SplineScene } from "@/components/ui/splite";
import { cn } from "@/lib/utils";

interface LoginFormProps {
    onLogin: (isVoice: boolean) => void;
}

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
    return (
        <input
            type={type}
            data-slot="input"
            className={cn(
                "file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input flex h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
                "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
                "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
                className
            )}
            {...props}
        />
    )
}

// 3D Background Component with Centered Robo
const SplineBackground: React.FC = () => {
    return (
        <div className="absolute inset-0 w-full h-full overflow-hidden bg-black">
            {/* Gradient Overlay for blue depth matching reference */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-900/20 via-black/80 to-black z-0" />

            <div className="absolute inset-0 z-0 flex items-center justify-center scale-100 md:scale-125">
                <SplineScene
                    scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
                    className="w-full h-full"
                />
            </div>

            {/* Vignette */}
            <div className="absolute inset-0 bg-black/60 z-10 pointer-events-none" />
        </div>
    );
};

export function GamingLogin({ onLogin }: LoginFormProps) {
    const [showPassword, setShowPassword] = useState(false);
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [focusedInput, setFocusedInput] = useState<string | null>(null);

    // Voice Auth State
    const [isListening, setIsListening] = useState(false);
    const [voiceStatus, setVoiceStatus] = useState("");

    // For 3D card effect
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);
    const rotateX = useTransform(mouseY, [-300, 300], [10, -10]);
    const rotateY = useTransform(mouseX, [-300, 300], [-10, 10]);

    const handleMouseMove = (e: React.MouseEvent) => {
        const rect = e.currentTarget.getBoundingClientRect();
        mouseX.set(e.clientX - rect.left - rect.width / 2);
        mouseY.set(e.clientY - rect.top - rect.height / 2);
    };

    const handleMouseLeave = () => {
        mouseX.set(0);
        mouseY.set(0);
    };

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setIsLoading(true);

        // Simulate API
        await new Promise(resolve => setTimeout(resolve, 1500));

        if (username === "Thamim" && password === "123") {
            onLogin(false);
        } else {
            alert("Incorrect credentials. Try 'Thamim' & '123'");
            setIsLoading(false);
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
        recognition.interimResults = false;

        setIsListening(true);
        setVoiceStatus("Listening...");

        recognition.onstart = () => {
            console.log("Voice recognition started");
        };

        recognition.onresult = (event: any) => {
            const transcript = event.results[0][0].transcript.toLowerCase();

            if (transcript.includes("log") || transcript.includes("login") || transcript.includes("enter") || transcript.includes("open") || transcript.includes("access")) {
                setVoiceStatus("Verified");
                setTimeout(() => {
                    onLogin(true);
                }, 800);
            } else {
                setVoiceStatus("Failed");
                setTimeout(() => {
                    setIsListening(false);
                    setVoiceStatus("");
                }, 2000);
            }
        };

        recognition.onerror = () => {
            setIsListening(false);
            setVoiceStatus("Error");
        };

        recognition.onend = () => {
            if (voiceStatus !== "Verified") {
                setIsListening(false);
            }
        };

        try {
            recognition.start();
        } catch (err) {
            setIsListening(false);
        }
    }

    return (
        <div className="relative min-h-screen w-full flex items-center justify-center overflow-hidden font-sans">
            <SplineBackground />

            {/* Transparent Container for 3D effect */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="w-full max-w-[380px] relative z-20 p-4"
                style={{ perspective: 1500 }}
            >
                <motion.div
                    className="relative"
                    style={{ rotateX, rotateY }}
                    onMouseMove={handleMouseMove}
                    onMouseLeave={handleMouseLeave}
                    whileHover={{ z: 10 }}
                >
                    <div className="relative group">
                        {/* Card glow effect */}
                        <motion.div
                            className="absolute -inset-[1px] rounded-2xl opacity-0 group-hover:opacity-70 transition-opacity duration-700"
                            animate={{
                                boxShadow: [
                                    "0 0 10px 2px rgba(255,255,255,0.03)",
                                    "0 0 15px 5px rgba(255,255,255,0.05)",
                                    "0 0 10px 2px rgba(255,255,255,0.03)"
                                ],
                                opacity: [0.2, 0.4, 0.2]
                            }}
                            transition={{
                                duration: 4,
                                repeat: Infinity,
                                ease: "easeInOut",
                                repeatType: "mirror"
                            }}
                        />

                        {/* Traveling light beam effect */}
                        <div className="absolute -inset-[1px] rounded-2xl overflow-hidden pointer-events-none">
                            <motion.div
                                className="absolute top-0 left-0 h-[2px] w-[50%] bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-70"
                                animate={{ left: ["-50%", "100%"] }}
                                transition={{ duration: 2.5, repeat: Infinity, ease: "linear" }}
                            />
                            <motion.div
                                className="absolute bottom-0 right-0 h-[2px] w-[50%] bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-70"
                                animate={{ right: ["-50%", "100%"] }}
                                transition={{ duration: 2.5, repeat: Infinity, ease: "linear", delay: 1.25 }}
                            />
                        </div>

                        {/* Glass card background - Transparent */}
                        <div className="relative bg-black/20 backdrop-blur-md rounded-2xl p-8 border border-white/10 shadow-2xl overflow-hidden min-h-[500px] flex flex-col justify-center">

                            {/* Logo and header */}
                            <div className="text-center space-y-2 mb-8">
                                <motion.h1
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.2 }}
                                    className="text-3xl font-bold text-white tracking-tight"
                                >
                                    Welcome Back
                                </motion.h1>

                                <motion.p
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: 0.3 }}
                                    className="text-white/60 text-sm"
                                >
                                    Enter your credentials to access system
                                </motion.p>
                            </div>

                            {/* Login form */}
                            <form onSubmit={handleSubmit} className="space-y-6">
                                <div className="space-y-4">
                                    {/* Username input */}
                                    <div className="relative group/input">
                                        <label className="text-xs text-white/50 ml-1 mb-1 block">Username</label>
                                        <div className="relative flex items-center">
                                            <User className={`absolute left-3 w-4 h-4 transition-colors ${focusedInput === 'username' ? 'text-white' : 'text-white/40'}`} />
                                            <Input
                                                type="text"
                                                placeholder="Enter username"
                                                value={username}
                                                onChange={(e) => setUsername(e.target.value)}
                                                onFocus={() => setFocusedInput("username")}
                                                onBlur={() => setFocusedInput(null)}
                                                className="pl-10 h-11 bg-white/5 border-white/10 text-white placeholder:text-white/20 focus:bg-white/10 transition-all rounded-xl"
                                            />
                                        </div>
                                    </div>

                                    {/* Password input */}
                                    <div className="relative group/input">
                                        <label className="text-xs text-white/50 ml-1 mb-1 block">Password</label>
                                        <div className="relative flex items-center">
                                            <Lock className={`absolute left-3 w-4 h-4 transition-colors ${focusedInput === 'password' ? 'text-white' : 'text-white/40'}`} />
                                            <Input
                                                type={showPassword ? "text" : "password"}
                                                placeholder="Enter password"
                                                value={password}
                                                onChange={(e) => setPassword(e.target.value)}
                                                onFocus={() => setFocusedInput("password")}
                                                onBlur={() => setFocusedInput(null)}
                                                className="pl-10 pr-10 h-11 bg-white/5 border-white/10 text-white placeholder:text-white/20 focus:bg-white/10 transition-all rounded-xl"
                                            />
                                            <div
                                                onClick={() => setShowPassword(!showPassword)}
                                                className="absolute right-3 cursor-pointer p-1"
                                            >
                                                {showPassword ? (
                                                    <EyeOff className="w-4 h-4 text-white/40 hover:text-white transition-colors" />
                                                ) : (
                                                    <Eye className="w-4 h-4 text-white/40 hover:text-white transition-colors" />
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Verify User button */}
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    type="submit"
                                    disabled={isLoading}
                                    className="w-full relative group/button overflow-hidden rounded-xl h-12 mt-2"
                                >
                                    <div className="absolute inset-0 bg-blue-600 hover:bg-blue-500 transition-colors duration-300" />
                                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover/button:translate-x-[100%] transition-transform duration-700 ease-in-out" />

                                    <span className="relative flex items-center justify-center gap-2 text-white font-semibold">
                                        {isLoading ? (
                                            <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        ) : (
                                            <>
                                                Verify User <ArrowRight className="w-4 h-4" />
                                            </>
                                        )}
                                    </span>
                                </motion.button>

                                <div className="relative flex py-2 items-center">
                                    <div className="flex-grow border-t border-white/10"></div>
                                    <span className="flex-shrink-0 mx-4 text-white/30 text-xs uppercase tracking-wider">OR</span>
                                    <div className="flex-grow border-t border-white/10"></div>
                                </div>

                                {/* Voice Auth */}
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    type="button"
                                    onClick={handleVoiceAuth}
                                    disabled={isListening}
                                    className={`w-full h-12 rounded-xl border border-white/10 flex items-center justify-center gap-2 transition-all ${isListening ? 'bg-red-500/10 border-red-500 text-red-500' : 'bg-white/5 hover:bg-white/10 text-white'}`}
                                >
                                    <Mic className={`w-4 h-4 ${isListening ? 'animate-pulse' : ''}`} />
                                    <span className="font-medium text-sm">
                                        {isListening ? (voiceStatus || "Listening...") : "Voice Authentication"}
                                    </span>
                                </motion.button>
                            </form>
                        </div>
                    </div>
                </motion.div>
            </motion.div>
        </div>
    );
}
