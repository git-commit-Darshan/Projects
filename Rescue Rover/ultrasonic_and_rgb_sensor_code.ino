#include <Wire.h>

#define I2C_ADDRESS 0x0A
volatile char statusChar = 'C';  

volatile bool gotRequest = false;
volatile unsigned long requestCount = 0;

// TCS3200 pins
const byte TCS_OUT_PIN = 2;
const byte TCS_S2_PIN  = 4;
const byte TCS_S3_PIN  = 5;
const byte TCS_S0_PIN  = 7;
const byte TCS_S1_PIN  = 8;

// Ultrasonic pins
const byte TRIG_PIN = 9;
const byte ECHO_PIN = 3;


const unsigned long COLOR_PHASE_MS   = 30;  
const unsigned long BLUE_HOLD_MS     = 200;  
const unsigned long PING_INTERVAL_MS = 60;   
const float CLOSE_RANGE_CM           = 7.0;  
const unsigned long CLOSE_HOLD_MS    = 200;  

unsigned long lastBlueSeenMs   = 0;
unsigned long lastCloseSeenMs  = 0;

enum ColorPhase { CP_RED, CP_BLUE, CP_GREEN };
volatile unsigned long tcsPulseCount = 0;    

ColorPhase currentPhase         = CP_RED;
unsigned long phaseStartMs      = 0;
unsigned long redCount          = 0;
unsigned long blueCount         = 0;
unsigned long greenCount        = 0;
bool colorSampleReady           = false;     
bool blueActive                 = false;     

enum UsState { US_IDLE, US_TRIG_HIGH, US_WAIT_ECHO };

UsState usState                 = US_IDLE;
unsigned long lastPingMs        = 0;
unsigned long trigStartUs       = 0;

volatile unsigned long echoRiseUs  = 0;
volatile unsigned long echoFallUs  = 0;
volatile bool echoDone             = false;

float lastDistanceCm            = -1.0;
bool ultrasonicClose            = false;    

void setupColorSensor();
void updateColorSensor(unsigned long now);
void evaluateBlue(unsigned long now);

void setupUltrasonic();
void updateUltrasonic(unsigned long now);

float distanceFromEchoUs(unsigned long dtUs);
void onI2CRequest();

void tcsOnPulse() {
  tcsPulseCount++;
}

void onEchoChange() {
  if (digitalRead(ECHO_PIN) == HIGH) {
    echoRiseUs = micros();
  } else {
    echoFallUs = micros();
    if (echoFallUs > echoRiseUs) {
      echoDone = true;
    }
  }
}

void setup() {
  // RGB Pins
  pinMode(TCS_OUT_PIN, INPUT);
  pinMode(TCS_S2_PIN,  OUTPUT);
  pinMode(TCS_S3_PIN,  OUTPUT);
  pinMode(TCS_S0_PIN,  OUTPUT);
  pinMode(TCS_S1_PIN,  OUTPUT);

  setupColorSensor();

  attachInterrupt(digitalPinToInterrupt(TCS_OUT_PIN), tcsOnPulse, RISING);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  setupUltrasonic();
  attachInterrupt(digitalPinToInterrupt(ECHO_PIN), onEchoChange, CHANGE);

  // I2C
  Wire.begin(I2C_ADDRESS);
  Wire.onRequest(onI2CRequest);

  Serial.begin(9600);
  Serial.println("Sensor slave 0x0A (US + RGB) started");

  pinMode(LED_BUILTIN, OUTPUT);

  unsigned long now = millis();
  phaseStartMs = now;
}

void loop() {
  unsigned long now = millis();

  updateColorSensor(now);
  updateUltrasonic(now);

  char newStatus;
  if (blueActive) {
    newStatus = 'G';
  } else if (ultrasonicClose) {
    newStatus = 'O';
  } else {
    newStatus = 'C';
  }

  statusChar = newStatus; 

  static unsigned long lastDebug = 0;
  if (now - lastDebug > 500) {
    lastDebug = now;
    Serial.print("blueActive=");
    Serial.print(blueActive);
    Serial.print("  ultrasonicClose=");
    Serial.print(ultrasonicClose);
    Serial.print("  lastDistanceCm=");
    Serial.print(lastDistanceCm);
    Serial.print("  statusChar=");
    Serial.println(statusChar);
  }

  static unsigned long ledOffTime = 0;
  if (gotRequest) {
    gotRequest = false;
    digitalWrite(LED_BUILTIN, HIGH);
    ledOffTime = now + 50;
  }
  if (digitalRead(LED_BUILTIN) == HIGH && now >= ledOffTime) {
    digitalWrite(LED_BUILTIN, LOW);
  }
}

void onI2CRequest() {
  Wire.write(statusChar);   
  requestCount++;
  gotRequest = true;
}

void setupColorSensor() {
  digitalWrite(TCS_S0_PIN, HIGH);
  digitalWrite(TCS_S1_PIN, LOW);

  currentPhase = CP_RED;
  phaseStartMs = millis();
  tcsPulseCount = 0;

  digitalWrite(TCS_S2_PIN, LOW);
  digitalWrite(TCS_S3_PIN, LOW);
}

void updateColorSensor(unsigned long now) {
  if (now - phaseStartMs >= COLOR_PHASE_MS) {
    unsigned long count = tcsPulseCount;
    tcsPulseCount = 0;
    phaseStartMs = now;

    switch (currentPhase) {
      case CP_RED:
        redCount = count;
        currentPhase = CP_BLUE;
        digitalWrite(TCS_S2_PIN, LOW);
        digitalWrite(TCS_S3_PIN, HIGH);
        break;

      case CP_BLUE:
        blueCount = count;
        currentPhase = CP_GREEN;
        digitalWrite(TCS_S2_PIN, HIGH);
        digitalWrite(TCS_S3_PIN, HIGH);
        break;

      case CP_GREEN:
        greenCount = count;
        colorSampleReady = true;
        currentPhase = CP_RED;
        digitalWrite(TCS_S2_PIN, LOW);
        digitalWrite(TCS_S3_PIN, LOW);
        break;
    }
  }

  if (colorSampleReady) {
    colorSampleReady = false;
    evaluateBlue(now);
  }
}

void evaluateBlue(unsigned long now) {
  bool isBlue = false;

  if (blueCount > 0 || redCount > 0 || greenCount > 0) {
    const float ratio = 1.4f;

    bool blueVsRed   = (float)blueCount > (float)redCount * ratio;
    bool blueVsGreen = (float)blueCount > (float)greenCount * ratio;

    isBlue = blueVsRed && blueVsGreen;
  }

  Serial.print("RGB pulses  R=");
  Serial.print(redCount);
  Serial.print(" G=");
  Serial.print(greenCount);
  Serial.print(" B=");
  Serial.print(blueCount);
  Serial.print(" -> isBlue=");
  Serial.println(isBlue ? "YES" : "NO");

  if (isBlue) {
    blueActive = true;
    lastBlueSeenMs = now;
  } else {
    if (blueActive && (now - lastBlueSeenMs > BLUE_HOLD_MS)) {
      blueActive = false;
    }
  }
}

void setupUltrasonic() {
  digitalWrite(TRIG_PIN, LOW);
  usState      = US_IDLE;
  lastPingMs   = millis();
  echoDone     = false;
  lastDistanceCm = -1.0;
}

void updateUltrasonic(unsigned long now) {
  unsigned long nowUs = micros();

  switch (usState) {
    case US_IDLE:
      if (now - lastPingMs >= PING_INTERVAL_MS) {
        lastPingMs = now;
        digitalWrite(TRIG_PIN, HIGH);
        trigStartUs = nowUs;
        usState = US_TRIG_HIGH;
      }
      break;

    case US_TRIG_HIGH:
      if ((unsigned long)(nowUs - trigStartUs) >= 10) {
        digitalWrite(TRIG_PIN, LOW);
        usState = US_WAIT_ECHO;
        echoDone = false;
      }
      break;

    case US_WAIT_ECHO:
      if (echoDone) {
        echoDone = false;
        unsigned long dtUs;
        if (echoFallUs > echoRiseUs) {
          dtUs = echoFallUs - echoRiseUs;
          lastDistanceCm = distanceFromEchoUs(dtUs);
        } else {
          lastDistanceCm = -1.0;
        }
        usState = US_IDLE;
      } else {
        if ((unsigned long)(nowUs - trigStartUs) > 30000UL) { 
          lastDistanceCm = -1.0;
          usState = US_IDLE;
        }
      }
      break;
  }

  if (lastDistanceCm > 0 && lastDistanceCm <= CLOSE_RANGE_CM) {
    ultrasonicClose = true;
    lastCloseSeenMs = now;
  } else if (ultrasonicClose && (now - lastCloseSeenMs > CLOSE_HOLD_MS)) {
    ultrasonicClose = false;
  }
}

float distanceFromEchoUs(unsigned long dtUs) {
  return dtUs / 58.0f;
}
