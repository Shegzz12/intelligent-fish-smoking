/**
 * Intelligent Fish Smoking - ESP32 Telemetry & Relay Client
 * 
 * This program connects to your Wi-Fi network and prompts you via the Serial Monitor
 * to input sensor values. It then builds a JSON payload, posts it to your server 
 * hosted on Render, parses the server's relay instruction, and toggles a physical relay/LED.
 */

#include <WiFi.h>
#include <HTTPClient.h>

// =====================================================================
// 1. CONFIGURATION (Modify these values)
// =====================================================================
const char* ssid = "YOUR_WIFI_SSID";             // Replace with your Wi-Fi SSID
const char* password = "YOUR_WIFI_PASSWORD";     // Replace with your Wi-Fi Password

// Paste your Render URL here when hosted (Do NOT include a trailing slash)
const String serverUrl = "https://YOUR-APP-NAME.onrender.com/api/telemetry";

// Define the GPIO pins for the physical components
#define RELAY_PIN 22        // GPIO pin connected to your physical relay
#define BOARD_LED_PIN 2     // Onboard blue LED for visual status feedback

// =====================================================================
// Helper function to read float values interactively from Serial Monitor
// =====================================================================
float readSerialFloat(String prompt) {
  Serial.print(prompt + " > ");
  
  // Clear any leftover data in buffer
  while (Serial.available() > 0) {
    Serial.read();
  }
  
  // Wait for user to start typing
  while (Serial.available() == 0) {
    delay(100);
  }
  
  // Read the float value
  float val = Serial.parseFloat();
  
  // Echo the received value back to the monitor
  Serial.println(val);
  
  // Consume any trailing newline/carriage return characters
  delay(50);
  while (Serial.available() > 0) {
    Serial.read();
  }
  
  return val;
}

// =====================================================================
// Setup Function
// =====================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(BOARD_LED_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW); // Default relay to OFF
  digitalWrite(BOARD_LED_PIN, LOW);

  Serial.println("\n==================================================");
  Serial.println("Intelligent Fish Smoking ESP32 Simulator Started");
  Serial.println("==================================================");

  // Connect to Wi-Fi
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi Connected successfully!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

// =====================================================================
// Main Interactive Loop
// =====================================================================
void loop() {
  // Ensure we are connected to Wi-Fi before continuing
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi connection lost! Reconnecting...");
    WiFi.disconnect();
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(".");
    }
    Serial.println("\nWiFi Reconnected!");
  }

  Serial.println("\n--- [START] Enter Telemetry Values below: ---");
  
  // Prompt and collect sensor parameters interactively
  float ovenTemp     = readSerialFloat("1. Oven Temperature (MAX6675, °C)");
  float dhtTemp      = readSerialFloat("2. Room Temperature (DHT11, °C)");
  float dhtHumidity  = readSerialFloat("3. Room Humidity (DHT11, %)");
  float mq6Adc       = readSerialFloat("4. Smoke ADC Reading (MQ6)");
  float mq6Ratio     = readSerialFloat("5. Smoke Ratio (MQ6)");
  float fishWeight   = readSerialFloat("6. Fish Weight (g)");

  Serial.println("\nSending telemetry to backend server...");
  Serial.println("Endpoint: " + serverUrl);

  // Construct standard JSON payload without requiring external libraries
  String jsonPayload = "{";
  jsonPayload += "\"oven_temp_c\":" + String(ovenTemp, 2) + ",";
  jsonPayload += "\"dht11_temp_c\":" + String(dhtTemp, 2) + ",";
  jsonPayload += "\"dht11_humidity_pct\":" + String(dhtHumidity, 2) + ",";
  jsonPayload += "\"mq6_adc\":" + String(mq6Adc, 2) + ",";
  jsonPayload += "\"mq6_ratio\":" + String(mq6Ratio, 2) + ",";
  jsonPayload += "\"weight_g\":" + String(fishWeight, 2);
  jsonPayload += "}";

  Serial.println("Payload: " + jsonPayload);

  // Set up the HTTP Request
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");

  // Send POST request
  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode > 0) {
    Serial.print("HTTP Status Code: ");
    Serial.println(httpResponseCode);

    String responseBody = http.getString();
    Serial.println("Server Response: " + responseBody);

    // Dependency-free JSON Parsing
    // Search the response string for the "relay_state" parameter
    if (responseBody.indexOf("\"relay_state\":\"ON\"") != -1) {
      Serial.println(">>> Command Received: Turn Relay ON! <<<");
      digitalWrite(RELAY_PIN, HIGH);
      digitalWrite(BOARD_LED_PIN, HIGH); // Visual confirmation on board
    } 
    else if (responseBody.indexOf("\"relay_state\":\"OFF\"") != -1) {
      Serial.println(">>> Command Received: Turn Relay OFF! <<<");
      digitalWrite(RELAY_PIN, LOW);
      digitalWrite(BOARD_LED_PIN, LOW);
    } 
    else {
      Serial.println("Warning: Relay state not recognized in response.");
    }
  } 
  else {
    Serial.print("Error sending HTTP POST. Code: ");
    Serial.println(httpResponseCode);
    Serial.println("Please check your Internet connection or Server URL.");
  }

  // Close HTTP connection
  http.end();

  Serial.println("\n--- [END] Process Completed. ---");
  Serial.println("Press ENTER or input characters on the Serial Monitor to start a new reading.\n");
  
  // Wait until user interacts to start another prompt cycle
  while (Serial.available() == 0) {
    delay(200);
  }
}
