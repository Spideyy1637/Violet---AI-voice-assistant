import React, { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Mic, Send, Paperclip, X } from "lucide-react";

interface ChatInputProps {
    onSend: (message: string) => void;
    onToggleListening: () => void;
    isListening: boolean;
    isLoading: boolean;
    disabled?: boolean;
    className?: string;
    placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
    onSend,
    onToggleListening,
    isListening,
    isLoading,
    disabled = false,
    className,
    placeholder = "Message Violet..."
}) => {
    const [value, setValue] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setValue(e.target.value);
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (value.trim() && !disabled) {
                onSend(value.trim());
                setValue("");
                if (textareaRef.current) textareaRef.current.style.height = "auto";
            }
        }
    };

    return (
        <div className={cn("relative w-full max-w-3xl mx-auto", className)}>
            <div className={cn(
                "relative flex items-end gap-2 p-2 rounded-[26px] border transition-all duration-300 shadow-lg",
                "bg-white/80 dark:bg-black/80 backdrop-blur-xl",
                "border-black/5 dark:border-white/10",
                "focus-within:border-violet-500/50 focus-within:ring-2 focus-within:ring-violet-500/20"
            )}>
                {/* Upload Button (Visual Only for now) */}
                <button
                    className="p-3 rounded-full hover:bg-black/5 dark:hover:bg-white/10 text-neutral-400 transition-colors"
                >
                    <Paperclip className="w-5 h-5" />
                </button>

                {/* Text Input */}
                <textarea
                    ref={textareaRef}
                    value={value}
                    onChange={handleInput}
                    onKeyDown={handleKeyDown}
                    placeholder={placeholder}
                    rows={1}
                    className={cn(
                        "w-full max-h-[200px] bg-transparent border-none focus:ring-0 resize-none py-3 text-base",
                        "text-neutral-900 dark:text-neutral-100",
                        "placeholder:text-neutral-400"
                    )}
                    disabled={disabled}
                />

                {/* Right Actions */}
                <div className="flex items-center gap-1 pb-1">
                    {value.trim() ? (
                        <button
                            onClick={() => {
                                onSend(value.trim());
                                setValue("");
                            }}
                            disabled={disabled}
                            className="p-2 bg-violet-600 text-white rounded-full hover:bg-violet-700 transition-all shadow-md active:scale-95"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    ) : (
                        <button
                            onClick={onToggleListening}
                            className={cn(
                                "p-2 rounded-full transition-all duration-300 active:scale-95",
                                isListening
                                    ? "bg-red-500 text-white animate-pulse shadow-red-500/20 shadow-lg"
                                    : "bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/20 text-neutral-600 dark:text-neutral-300"
                            )}
                        >
                            {isListening ? (
                                <span className="w-5 h-5 flex items-center justify-center font-bold">●</span>
                            ) : (
                                <Mic className="w-5 h-5" />
                            )}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};
