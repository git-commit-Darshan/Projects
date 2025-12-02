#include <Wire.h>
#define SLAVE_ADDR 0x09

// Motor pins
const int forwardPinA   = 8;   // Yellow Lego
const int backwardPinA  = 12;
const int forwardPinA2  = 7;   // Orange Lego (reversed orientation)
const int backwardPinA2 = 4;

const int forwardPinB   = 9;   // Tan Lego
const int backwardPinB  = 11;
const int forwardPinB2  = 6;   // Brown Lego
const int backwardPinB2 = 5;

// ON/OFF button + debounce
const int buttonPin = 3;

int  buttonState        = LOW;
int  lastButtonState    = LOW;
int  idleLevel          = LOW;   
bool onOff              = true;  

unsigned long lastDebounceTime    = 0;
const unsigned long debounceDelay = 50;

char currentCmd = 'G';  

const unsigned long FORWARD_ON_MS  = 80;  // time motors ON in each cycle
const unsigned long FORWARD_OFF_MS = 40;  // time motors OFF in each cycle

bool forwardPhaseOn                = true;
unsigned long forwardPhaseStartMs  = 0;

void onRequestHandler() {
  Wire.write(onOff ? 1 : 0);
}

void onReceiveHandler() {
  while (Wire.available()) {
    char cmd = (char)Wire.read();
    Serial.print("Received cmd from master: ");
    Serial.println(cmd);
    currentCmd = cmd;

    if (currentCmd != 'C') {
      forwardPhaseOn = true;
      forwardPhaseStartMs = millis();
    }
  }
}

void setup() {
  Serial.begin(9600);

  Wire.begin(SLAVE_ADDR);
  Wire.onReceive(onReceiveHandler);
  Wire.onRequest(onRequestHandler);

  pinMode(buttonPin, INPUT);

  unsigned long settleStart = millis();
  while (millis() - settleStart < 10) {
  }

  idleLevel       = digitalRead(buttonPin);
  buttonState     = idleLevel;
  lastButtonState = idleLevel;
  Serial.print("Button idle level detected as: ");
  Serial.println(idleLevel);

  // Motor pins
  pinMode(forwardPinA,  OUTPUT);
  pinMode(backwardPinA, OUTPUT);
  pinMode(forwardPinA2, OUTPUT);
  pinMode(backwardPinA2, OUTPUT);

  pinMode(forwardPinB,  OUTPUT);
  pinMode(backwardPinB, OUTPUT);
  pinMode(forwardPinB2, OUTPUT);
  pinMode(backwardPinB2, OUTPUT);

  stopMotors();
  forwardPhaseStartMs = millis();
}

void loop() {
  unsigned long now = millis();

  int reading = digitalRead(buttonPin);

  if (reading != lastButtonState) {
    lastDebounceTime = now;
  }

  if ((now - lastDebounceTime) > debounceDelay) {
    if (reading != buttonState) {
      buttonState = reading;

      if (buttonState != idleLevel) {
        onOff = !onOff;
        Serial.print("Toggled onOff to: ");
        Serial.println(onOff ? "ON" : "OFF");
      }
    }
  }

  lastButtonState = reading;

  if (!onOff) {
    stopMotors();
    return;
  }

  switch (currentCmd) {
    case 'C': {
      unsigned long elapsed = now - forwardPhaseStartMs;

      if (forwardPhaseOn) {
        if (elapsed >= FORWARD_ON_MS) {
          forwardPhaseOn = false;
          forwardPhaseStartMs = now;
          stopMotors();
        } else {
          moveForward();
        }
      } else {
        if (elapsed >= FORWARD_OFF_MS) {
          forwardPhaseOn = true;
          forwardPhaseStartMs = now;
          moveForward();
        } else {
          stopMotors();
        }
      }
      break;
    }

    case 'R':   // reverse
      moveBackward();
      break;

    case 'O':   // border
      Serial.println("thats the border");
      rightTurn();
      break;

    case 'B':   // obstacle
      Serial.println("and thats obstacle");
      rightTurn();
      break;

    case 'G':   // goal 
    case 'S':  
    default:
      stopMotors();
      break;
  }
}

void moveForward() {
  digitalWrite(forwardPinA,  HIGH);
  digitalWrite(backwardPinA, LOW);
  digitalWrite(forwardPinA2, HIGH);
  digitalWrite(backwardPinA2, LOW);

  digitalWrite(forwardPinB,  HIGH);
  digitalWrite(backwardPinB, LOW);
  digitalWrite(forwardPinB2, HIGH);
  digitalWrite(backwardPinB2, LOW);
}

void moveBackward() {
  digitalWrite(forwardPinA,  LOW);
  digitalWrite(backwardPinA, HIGH);
  digitalWrite(forwardPinA2, LOW);
  digitalWrite(backwardPinA2, HIGH);

  digitalWrite(forwardPinB,  LOW);
  digitalWrite(backwardPinB, HIGH);
  digitalWrite(forwardPinB2, LOW);
  digitalWrite(backwardPinB2, HIGH);
}

void stopMotors() {
  digitalWrite(forwardPinA,  LOW);
  digitalWrite(backwardPinA, LOW);
  digitalWrite(forwardPinA2, LOW);
  digitalWrite(backwardPinA2, LOW);

  digitalWrite(forwardPinB,  LOW);
  digitalWrite(backwardPinB, LOW);
  digitalWrite(forwardPinB2, LOW);
  digitalWrite(backwardPinB2, LOW);
}

void rightTurn() {
  digitalWrite(forwardPinA,  LOW);
  digitalWrite(backwardPinA, LOW);
  digitalWrite(forwardPinA2, LOW);
  digitalWrite(backwardPinA2, LOW);

  digitalWrite(forwardPinB,  HIGH);
  digitalWrite(backwardPinB, LOW);
  digitalWrite(forwardPinB2, HIGH);
  digitalWrite(backwardPinB2, LOW);
}
