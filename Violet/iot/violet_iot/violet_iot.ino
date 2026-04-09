/*
 * ============================================
 * VIOLET IoT - ESP32 Smart Device Controller
 * ============================================
 * 
 * This sketch runs on an ESP32 board and creates
 * a Wi-Fi web server to control a 2-channel relay
 * module via HTTP requests from the VIOLET backend.
 * 
 * Hardware Connections:
 *   ESP32 GPIO 26 → Relay 1 IN (Light)
 *   ESP32 GPIO 27 → Relay 2 IN (Fan)
 *   ESP32 GND     → Relay GND
 *   ESP32 5V/VIN  → Relay VCC
 * 
 * Instructions:
 *   1. Update WIFI_SSID and WIFI_PASSWORD below
 *   2. Upload to ESP32 via Arduino IDE
 *   3. Open Serial Monitor (115200 baud)
 *   4. Note the IP address printed
 *   5. Update ESP32_IP in VIOLET's server.py
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// ============================================
// CONFIGURATION - UPDATE THESE VALUES
// ============================================
const char* WIFI_SSID     = "YOUR_WIFI_NAME";      // ← Change this
const char* WIFI_PASSWORD  = "YOUR_WIFI_PASSWORD";  // ← Change this

// ============================================
// RELAY PIN DEFINITIONS
// ============================================
// Most relay modules are ACTIVE LOW (LOW = ON, HIGH = OFF)
#define RELAY1_PIN  26   // Light
#define RELAY2_PIN  27   // Fan

// Set to true if your relay module is Active LOW (most common)
#define RELAY_ACTIVE_LOW  true

// ============================================
// GLOBAL VARIABLES
// ============================================
WebServer server(80);

// Device states (true = ON, false = OFF)
bool relay1State = false;  // Light
bool relay2State = false;  // Fan

// Device names for display
const char* relay1Name = "Light";
const char* relay2Name = "Fan";

// ============================================
// HELPER FUNCTIONS
// ============================================

// Set relay pin state (handles Active LOW logic)
void setRelay(int pin, bool state) {
  if (RELAY_ACTIVE_LOW) {
    digitalWrite(pin, state ? LOW : HIGH);  // Active LOW: LOW=ON, HIGH=OFF
  } else {
    digitalWrite(pin, state ? HIGH : LOW);  // Active HIGH: HIGH=ON, LOW=OFF
  }
}

// Add CORS headers to allow requests from VIOLET frontend
void addCorsHeaders() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
}

// ============================================
// HTTP ROUTE HANDLERS
// ============================================

// GET / — Home page with device status
void handleRoot() {
  addCorsHeaders();
  
  String html = "<!DOCTYPE html><html><head>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<title>VIOLET IoT Controller</title>";
  html += "<style>";
  html += "body { font-family: 'Segoe UI', sans-serif; background: #0f0a1a; color: #e0d4f5; ";
  html += "display: flex; flex-direction: column; align-items: center; padding: 40px; }";
  html += "h1 { color: #8b5cf6; margin-bottom: 30px; }";
  html += ".device { background: #1a1025; border: 1px solid #2d1f42; border-radius: 16px; ";
  html += "padding: 24px 32px; margin: 10px; width: 280px; text-align: center; }";
  html += ".device h2 { margin: 0 0 16px 0; font-size: 20px; }";
  html += ".status { font-size: 48px; margin: 10px 0; }";
  html += ".btn { display: inline-block; padding: 12px 32px; margin: 8px; border-radius: 12px; ";
  html += "text-decoration: none; font-weight: 600; font-size: 16px; border: none; cursor: pointer; }";
  html += ".btn-on { background: #22c55e; color: white; }";
  html += ".btn-off { background: #ef4444; color: white; }";
  html += ".label { font-size: 14px; color: #9ca3af; margin-top: 8px; }";
  html += ".badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: 600; }";
  html += ".badge-on { background: #22c55e30; color: #22c55e; }";
  html += ".badge-off { background: #ef444430; color: #ef4444; }";
  html += "</style></head><body>";
  
  html += "<h1>🟣 VIOLET IoT Controller</h1>";
  
  // Relay 1 - Light
  html += "<div class='device'>";
  html += "<h2>💡 " + String(relay1Name) + "</h2>";
  html += "<div class='status'>" + String(relay1State ? "🟢" : "🔴") + "</div>";
  html += "<span class='badge " + String(relay1State ? "badge-on'>ON" : "badge-off'>OFF") + "</span><br>";
  html += "<a href='/relay1/on' class='btn btn-on'>Turn ON</a>";
  html += "<a href='/relay1/off' class='btn btn-off'>Turn OFF</a>";
  html += "<p class='label'>GPIO " + String(RELAY1_PIN) + " → Relay 1</p>";
  html += "</div>";
  
  // Relay 2 - Fan
  html += "<div class='device'>";
  html += "<h2>🌀 " + String(relay2Name) + "</h2>";
  html += "<div class='status'>" + String(relay2State ? "🟢" : "🔴") + "</div>";
  html += "<span class='badge " + String(relay2State ? "badge-on'>ON" : "badge-off'>OFF") + "</span><br>";
  html += "<a href='/relay2/on' class='btn btn-on'>Turn ON</a>";
  html += "<a href='/relay2/off' class='btn btn-off'>Turn OFF</a>";
  html += "<p class='label'>GPIO " + String(RELAY2_PIN) + " → Relay 2</p>";
  html += "</div>";
  
  html += "<p class='label' style='margin-top: 30px;'>Connected to VIOLET Voice Assistant</p>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

// GET /status — JSON status (used by VIOLET backend)
void handleStatus() {
  addCorsHeaders();
  
  StaticJsonDocument<200> doc;
  doc["relay1"] = relay1State ? "ON" : "OFF";
  doc["relay2"] = relay2State ? "ON" : "OFF";
  doc["relay1_name"] = relay1Name;
  doc["relay2_name"] = relay2Name;
  doc["uptime"] = millis() / 1000;
  
  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

// Relay 1 Control
void handleRelay1On() {
  addCorsHeaders();
  relay1State = true;
  setRelay(RELAY1_PIN, true);
  Serial.println("✅ Relay 1 (Light) → ON");
  server.send(200, "application/json", "{\"relay1\": \"ON\", \"success\": true}");
}

void handleRelay1Off() {
  addCorsHeaders();
  relay1State = false;
  setRelay(RELAY1_PIN, false);
  Serial.println("❌ Relay 1 (Light) → OFF");
  server.send(200, "application/json", "{\"relay1\": \"OFF\", \"success\": true}");
}

// Relay 2 Control
void handleRelay2On() {
  addCorsHeaders();
  relay2State = true;
  setRelay(RELAY2_PIN, true);
  Serial.println("✅ Relay 2 (Fan) → ON");
  server.send(200, "application/json", "{\"relay2\": \"ON\", \"success\": true}");
}

void handleRelay2Off() {
  addCorsHeaders();
  relay2State = false;
  setRelay(RELAY2_PIN, false);
  Serial.println("❌ Relay 2 (Fan) → OFF");
  server.send(200, "application/json", "{\"relay2\": \"OFF\", \"success\": true}");
}

// Handle OPTIONS preflight
void handleCors() {
  addCorsHeaders();
  server.send(204);
}

// ============================================
// SETUP
// ============================================
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println();
  Serial.println("╔══════════════════════════════════════╗");
  Serial.println("║   VIOLET IoT - ESP32 Controller      ║");
  Serial.println("╚══════════════════════════════════════╝");
  
  // Initialize relay pins
  pinMode(RELAY1_PIN, OUTPUT);
  pinMode(RELAY2_PIN, OUTPUT);
  
  // Start with relays OFF
  setRelay(RELAY1_PIN, false);
  setRelay(RELAY2_PIN, false);
  
  Serial.println("🔌 Relay pins initialized (GPIO 26, 27)");
  
  // Connect to Wi-Fi
  Serial.print("📡 Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✅ WiFi Connected!");
    Serial.print("🌐 ESP32 IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.println();
    Serial.println("╔══════════════════════════════════════╗");
    Serial.print("║  Use this IP in server.py: ");
    Serial.print(WiFi.localIP());
    Serial.println("  ║");
    Serial.println("╚══════════════════════════════════════╝");
  } else {
    Serial.println();
    Serial.println("❌ WiFi Connection Failed! Check SSID and Password.");
    Serial.println("   Restarting in 5 seconds...");
    delay(5000);
    ESP.restart();
  }
  
  // Register HTTP routes
  server.on("/", HTTP_GET, handleRoot);
  server.on("/status", HTTP_GET, handleStatus);
  server.on("/relay1/on", HTTP_GET, handleRelay1On);
  server.on("/relay1/off", HTTP_GET, handleRelay1Off);
  server.on("/relay2/on", HTTP_GET, handleRelay2On);
  server.on("/relay2/off", HTTP_GET, handleRelay2Off);
  
  // CORS preflight
  server.on("/status", HTTP_OPTIONS, handleCors);
  server.on("/relay1/on", HTTP_OPTIONS, handleCors);
  server.on("/relay1/off", HTTP_OPTIONS, handleCors);
  server.on("/relay2/on", HTTP_OPTIONS, handleCors);
  server.on("/relay2/off", HTTP_OPTIONS, handleCors);
  
  // Start server
  server.begin();
  Serial.println("🚀 HTTP Server started on port 80");
  Serial.println("📋 Available endpoints:");
  Serial.println("   GET /          → Web Dashboard");
  Serial.println("   GET /status    → JSON Status");
  Serial.println("   GET /relay1/on → Light ON");
  Serial.println("   GET /relay1/off→ Light OFF");
  Serial.println("   GET /relay2/on → Fan ON");
  Serial.println("   GET /relay2/off→ Fan OFF");
  Serial.println();
  Serial.println("Ready for VIOLET voice commands! 🎤");
}

// ============================================
// MAIN LOOP
// ============================================
void loop() {
  server.handleClient();
  
  // Reconnect Wi-Fi if disconnected
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi lost! Reconnecting...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
      delay(500);
      Serial.print(".");
      attempts++;
    }
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n✅ Reconnected! IP: " + WiFi.localIP().toString());
    }
  }
}
