/*
  =============================================================================
  Real-Time Human Emotion Recognition - Arduino LED Controller
  =============================================================================
  
  Hardware Wiring Guide:
  ---------------------
  Pin 2 -> 220 Ohm Resistor -> Anode (+) of HAPPY LED (Green)  -> Cathode (-) to GND
  Pin 3 -> 220 Ohm Resistor -> Anode (+) of SAD LED (Blue)     -> Cathode (-) to GND
  Pin 4 -> 220 Ohm Resistor -> Anode (+) of ANGRY LED (Red)    -> Cathode (-) to GND
  Pin 5 -> 220 Ohm Resistor -> Anode (+) of SURPRISE LED (Yel) -> Cathode (-) to GND
  Pin 6 -> 220 Ohm Resistor -> Anode (+) of NEUTRAL LED (Wht)  -> Cathode (-) to GND

  Baud Rate: 9600
  Commands received over Serial:
    "HAPPY\n"
    "SAD\n"
    "ANGRY\n"
    "SURPRISE\n"
    "NEUTRAL\n"
    "DISGUST\n"
    "FEAR\n"
    "NONE\n"
  =============================================================================
*/

// Pin Assignments
const int PIN_HAPPY    = 2; // Green LED
const int PIN_SAD      = 3; // Blue LED
const int PIN_ANGRY    = 4; // Red LED
const int PIN_SURPRISE = 5; // Yellow LED
const int PIN_NEUTRAL  = 6; // White/Orange LED

const int ALL_PINS[] = {PIN_HAPPY, PIN_SAD, PIN_ANGRY, PIN_SURPRISE, PIN_NEUTRAL};
const int NUM_PINS = 5;

// Buffer for incoming serial commands
String inputString = "";
bool stringComplete = false;

// Auto-timeout: turn off LEDs if no message received for 3 seconds
unsigned long lastCommandTime = 0;
const unsigned long TIMEOUT_MS = 3000;

void setup() {
  // Initialize Serial
  Serial.begin(9600);
  inputString.reserve(64);

  // Initialize LED Pins as OUTPUT
  for (int i = 0; i < NUM_PINS; i++) {
    pinMode(ALL_PINS[i], OUTPUT);
    digitalWrite(ALL_PINS[i], LOW);
  }

  // Startup Test Sequence (blink each LED once)
  for (int i = 0; i < NUM_PINS; i++) {
    digitalWrite(ALL_PINS[i], HIGH);
    delay(100);
    digitalWrite(ALL_PINS[i], LOW);
  }

  Serial.println("ARDUINO_READY");
}

void loop() {
  // Check if a full line was received
  if (stringComplete) {
    inputString.trim();
    inputString.toUpperCase();

    if (inputString.length() > 0) {
      handleEmotionCommand(inputString);
      lastCommandTime = millis();
    }

    inputString = "";
    stringComplete = false;
  }

  // Timeout check: turn off LEDs if face lost or python disconnected
  if (millis() - lastCommandTime > TIMEOUT_MS) {
    turnAllLedsOff();
  }
}

// Read serial data using SerialEvent
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n' || inChar == '\r') {
      if (inputString.length() > 0) {
        stringComplete = true;
      }
    } else {
      inputString += inChar;
    }
  }
}

void turnAllLedsOff() {
  for (int i = 0; i < NUM_PINS; i++) {
    digitalWrite(ALL_PINS[i], LOW);
  }
}

void handleEmotionCommand(String emotion) {
  turnAllLedsOff();

  if (emotion == "HAPPY") {
    digitalWrite(PIN_HAPPY, HIGH);
  } else if (emotion == "SAD") {
    digitalWrite(PIN_SAD, HIGH);
  } else if (emotion == "ANGRY") {
    digitalWrite(PIN_ANGRY, HIGH);
  } else if (emotion == "SURPRISE") {
    digitalWrite(PIN_SURPRISE, HIGH);
  } else if (emotion == "NEUTRAL") {
    digitalWrite(PIN_NEUTRAL, HIGH);
  } else if (emotion == "DISGUST" || emotion == "FEAR") {
    // Both mapped to Angry/Surprise warning indicator
    digitalWrite(PIN_ANGRY, HIGH);
  }
}
