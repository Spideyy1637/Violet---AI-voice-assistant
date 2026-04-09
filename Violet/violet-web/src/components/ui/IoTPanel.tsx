"use client";

import { useState, useEffect, useCallback } from "react";
import { X, Wifi, WifiOff, Lightbulb, Fan, RefreshCw } from "lucide-react";

interface DeviceState {
    name: string;
    state: boolean;
}

interface IoTStatus {
    connected: boolean;
    esp32_ip: string;
    devices: {
        light: DeviceState;
        fan: DeviceState;
    };
}

interface IoTPanelProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function IoTPanel({ isOpen, onClose }: IoTPanelProps) {
    const [status, setStatus] = useState<IoTStatus | null>(null);
    const [loading, setLoading] = useState(false);
    const [toggling, setToggling] = useState<string | null>(null);

    const getBackendUrl = () => {
        const protocol = window.location.protocol;
        const hostname = window.location.hostname;
        return `${protocol}//${hostname}:8001`;
    };

    const fetchStatus = useCallback(async () => {
        try {
            const res = await fetch(`${getBackendUrl()}/api/iot/status`);
            const data = await res.json();
            setStatus(data);
        } catch {
            setStatus(null);
        }
    }, []);

    // Poll status every 5s when panel is open
    useEffect(() => {
        if (!isOpen) return;
        fetchStatus();
        const interval = setInterval(fetchStatus, 5000);
        return () => clearInterval(interval);
    }, [isOpen, fetchStatus]);

    const toggleDevice = async (device: string) => {
        if (!status || toggling) return;
        const currentState = device === "light" ? status.devices.light.state : status.devices.fan.state;
        const newAction = currentState ? "off" : "on";

        setToggling(device);
        try {
            await fetch(`${getBackendUrl()}/api/iot/control`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ device, action: newAction }),
            });
            // Refresh status after toggle
            await fetchStatus();
        } catch (err) {
            console.error("IoT control error:", err);
        } finally {
            setToggling(null);
        }
    };

    const refreshStatus = async () => {
        setLoading(true);
        await fetchStatus();
        setLoading(false);
    };

    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div className="iot-backdrop" onClick={onClose} />

            {/* Panel */}
            <div className="iot-panel">
                {/* Header */}
                <div className="iot-panel-header">
                    <div className="iot-panel-title">
                        <span className="iot-title-icon">🏠</span>
                        <span>Smart Home</span>
                    </div>
                    <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                        <button className="iot-refresh-btn" onClick={refreshStatus} title="Refresh status">
                            <RefreshCw size={16} className={loading ? "iot-spinning" : ""} />
                        </button>
                        <button className="iot-close-btn" onClick={onClose}>
                            <X size={18} />
                        </button>
                    </div>
                </div>

                {/* Connection Status */}
                <div className={`iot-connection ${status?.connected ? "iot-connected" : "iot-disconnected"}`}>
                    {status?.connected ? <Wifi size={14} /> : <WifiOff size={14} />}
                    <span>{status?.connected ? "ESP32 Connected" : "ESP32 Offline"}</span>
                    {status?.esp32_ip && <span className="iot-ip">{status.esp32_ip}</span>}
                </div>

                {/* Devices */}
                <div className="iot-devices">
                    {/* Light Card */}
                    <div className={`iot-device-card ${status?.devices?.light?.state ? "iot-device-on" : ""}`}>
                        <div className="iot-device-icon-wrap">
                            <Lightbulb size={28} className={status?.devices?.light?.state ? "iot-icon-active" : "iot-icon-inactive"} />
                        </div>
                        <div className="iot-device-info">
                            <span className="iot-device-name">Light</span>
                            <span className={`iot-device-state ${status?.devices?.light?.state ? "iot-state-on" : "iot-state-off"}`}>
                                {status?.devices?.light?.state ? "ON" : "OFF"}
                            </span>
                        </div>
                        <button
                            className={`iot-toggle-btn ${status?.devices?.light?.state ? "iot-toggle-on" : "iot-toggle-off"}`}
                            onClick={() => toggleDevice("light")}
                            disabled={toggling === "light"}
                        >
                            <div className="iot-toggle-knob" />
                        </button>
                    </div>

                    {/* Fan Card */}
                    <div className={`iot-device-card ${status?.devices?.fan?.state ? "iot-device-on" : ""}`}>
                        <div className="iot-device-icon-wrap">
                            <Fan size={28} className={`${status?.devices?.fan?.state ? "iot-icon-active iot-fan-spinning" : "iot-icon-inactive"}`} />
                        </div>
                        <div className="iot-device-info">
                            <span className="iot-device-name">Fan</span>
                            <span className={`iot-device-state ${status?.devices?.fan?.state ? "iot-state-on" : "iot-state-off"}`}>
                                {status?.devices?.fan?.state ? "ON" : "OFF"}
                            </span>
                        </div>
                        <button
                            className={`iot-toggle-btn ${status?.devices?.fan?.state ? "iot-toggle-on" : "iot-toggle-off"}`}
                            onClick={() => toggleDevice("fan")}
                            disabled={toggling === "fan"}
                        >
                            <div className="iot-toggle-knob" />
                        </button>
                    </div>
                </div>

                {/* Voice tip */}
                <div className="iot-tip">
                    <span>💡</span>
                    <span>Try saying <strong>"Turn on the light"</strong> or <strong>"Turn off the fan"</strong></span>
                </div>
            </div>

            <style>{`
                .iot-backdrop {
                    position: fixed;
                    inset: 0;
                    background: rgba(0, 0, 0, 0.5);
                    backdrop-filter: blur(4px);
                    z-index: 998;
                    animation: iot-fadeIn 0.2s ease;
                }

                @keyframes iot-fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }

                .iot-panel {
                    position: fixed;
                    top: 0;
                    right: 0;
                    width: 360px;
                    max-width: 90vw;
                    height: 100vh;
                    background: var(--bg-deep, #0f0a1a);
                    border-left: 1px solid var(--glass-border, #2d1f42);
                    z-index: 999;
                    display: flex;
                    flex-direction: column;
                    padding: 24px;
                    animation: iot-slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                    overflow-y: auto;
                }

                @keyframes iot-slideIn {
                    from { transform: translateX(100%); }
                    to { transform: translateX(0); }
                }

                .iot-panel-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 24px;
                }

                .iot-panel-title {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    font-size: 20px;
                    font-weight: 700;
                    color: var(--text-primary, #e0d4f5);
                }

                .iot-title-icon {
                    font-size: 24px;
                }

                .iot-close-btn, .iot-refresh-btn {
                    width: 32px;
                    height: 32px;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: transparent;
                    border: 1px solid var(--glass-border, #2d1f42);
                    color: var(--text-muted, #9ca3af);
                    cursor: pointer;
                    transition: all 0.15s ease;
                }

                .iot-close-btn:hover, .iot-refresh-btn:hover {
                    background: var(--bg-surface, #1a1025);
                    color: var(--text-primary, #e0d4f5);
                }

                .iot-spinning {
                    animation: iot-spin 1s linear infinite;
                }

                @keyframes iot-spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }

                /* Connection Status */
                .iot-connection {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 10px 16px;
                    border-radius: 12px;
                    font-size: 13px;
                    font-weight: 500;
                    margin-bottom: 24px;
                }

                .iot-connected {
                    background: rgba(34, 197, 94, 0.1);
                    color: #22c55e;
                    border: 1px solid rgba(34, 197, 94, 0.2);
                }

                .iot-disconnected {
                    background: rgba(239, 68, 68, 0.1);
                    color: #ef4444;
                    border: 1px solid rgba(239, 68, 68, 0.2);
                }

                .iot-ip {
                    margin-left: auto;
                    font-family: monospace;
                    font-size: 12px;
                    opacity: 0.7;
                }

                /* Device Cards */
                .iot-devices {
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                }

                .iot-device-card {
                    display: flex;
                    align-items: center;
                    gap: 16px;
                    padding: 20px;
                    background: var(--bg-surface, #1a1025);
                    border: 1px solid var(--glass-border, #2d1f42);
                    border-radius: 16px;
                    transition: all 0.3s ease;
                }

                .iot-device-on {
                    border-color: rgba(139, 92, 246, 0.4);
                    box-shadow: 0 0 20px rgba(139, 92, 246, 0.1);
                }

                .iot-device-icon-wrap {
                    width: 52px;
                    height: 52px;
                    border-radius: 14px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: var(--bg-deep, #0f0a1a);
                    flex-shrink: 0;
                }

                .iot-icon-active {
                    color: #f59e0b;
                    filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.5));
                }

                .iot-icon-inactive {
                    color: var(--text-muted, #6b7280);
                }

                .iot-fan-spinning {
                    animation: iot-fanSpin 1.5s linear infinite;
                }

                @keyframes iot-fanSpin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }

                .iot-device-info {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }

                .iot-device-name {
                    font-size: 16px;
                    font-weight: 600;
                    color: var(--text-primary, #e0d4f5);
                }

                .iot-device-state {
                    font-size: 13px;
                    font-weight: 500;
                }

                .iot-state-on {
                    color: #22c55e;
                }

                .iot-state-off {
                    color: var(--text-muted, #6b7280);
                }

                /* Toggle Switch */
                .iot-toggle-btn {
                    width: 52px;
                    height: 28px;
                    border-radius: 14px;
                    border: none;
                    cursor: pointer;
                    position: relative;
                    transition: all 0.3s ease;
                    flex-shrink: 0;
                }

                .iot-toggle-on {
                    background: linear-gradient(135deg, #8b5cf6, #a78bfa);
                    box-shadow: 0 0 12px rgba(139, 92, 246, 0.4);
                }

                .iot-toggle-off {
                    background: #374151;
                }

                .iot-toggle-knob {
                    width: 22px;
                    height: 22px;
                    border-radius: 50%;
                    background: white;
                    position: absolute;
                    top: 3px;
                    transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                }

                .iot-toggle-on .iot-toggle-knob {
                    left: 27px;
                }

                .iot-toggle-off .iot-toggle-knob {
                    left: 3px;
                }

                .iot-toggle-btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }

                /* Voice Tip */
                .iot-tip {
                    display: flex;
                    align-items: flex-start;
                    gap: 10px;
                    margin-top: 32px;
                    padding: 14px 16px;
                    background: rgba(139, 92, 246, 0.08);
                    border: 1px solid rgba(139, 92, 246, 0.15);
                    border-radius: 12px;
                    font-size: 13px;
                    color: var(--text-secondary, #c4b5d4);
                    line-height: 1.5;
                }

                .iot-tip strong {
                    color: #a78bfa;
                }

                @media (max-width: 640px) {
                    .iot-panel {
                        width: 100%;
                        max-width: 100vw;
                    }
                }
            `}</style>
        </>
    );
}
