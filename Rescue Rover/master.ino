#include <Wire.h>
#include <LiquidCrystal.h>

const int BUZZER_PIN = 10;
const int LED_PINS[3] = {7, 8, 9};   

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

#define SENSOR_SLAVE_ADDR1 0x08   // IR tape sensor slave (sends 0/1)
#define SENSOR_SLAVE_ADDR2 0x09   // motor controller + on/off button slave
#define SENSOR_SLAVE_ADDR3 0x0A   // RGB + ultrasonic slave 

const unsigned long POLL_INTERVAL_MS   = 80;    
const unsigned long HEARTBEAT_INTERVAL = 2000;

unsigned long lastPollMs      = 0;
unsigned long lastHeartbeatMs = 0;

int  lastIRRaw        = -1;
char rawStatus3       = 'C';   
char stableStatus3    = 'C';   
char lastRawStatus3   = 'C';
int  sameRawCount3    = 0;

bool infraBlocked     = false; 
bool machineOn        = true;  

enum MoveMode {
  MOVE_NORMAL,
  MOVE_OBS_STOP,     
  MOVE_OBS_BACK,
  MOVE_OBS_TURN,
  MOVE_BORDER_BACK,  
  MOVE_BORDER_TURN
};

MoveMode moveMode         = MOVE_NORMAL;
unsigned long moveStartMs = 0;

const unsigned long OBST_STOP_MS    = 200;  
const unsigned long OBST_BACK_MS    = 600;  
const unsigned long OBST_TURN_MS    = 500;  
const unsigned long BORDER_BACK_MS  = 500;  
const unsigned long BORDER_TURN_MS  = 1000; 

int requestOneByte(byte addr) {
  Wire.requestFrom(addr, (uint8_t)1);
  if (Wire.available()) {
    return Wire.read();
  }
  return -1;
}

void sendByte(byte addr, byte b) {
  Serial.print("Sending '");
  Serial.write(b);
  Serial.print("' to 0x");
  Serial.println(addr, HEX);

  Wire.beginTransmission(addr);
  Wire.write(b);
  Wire.endTransmission();
}

bool updateMachineOnFrom09(bool current) {
  int r = requestOneByte(SENSOR_SLAVE_ADDR2);

  if (r >= 0) {
    Serial.print("From 0x09 (button): RAW=");
    Serial.println(r);

    if (r == 0) return false;  
    if (r == 1) return true;   

    Serial.println("Unexpected ON/OFF value; treating as ON");
    return true;
  }

  Serial.println("No valid byte from 0x09; treating as ON");
  return true;
}

void lcdHandler(char statusChar, bool infra, bool machineOn) {
  lcd.clear();

  if (statusChar == 'G') {
    // Goal object found
    lcd.setCursor(0, 0);
    lcd.print("Goal object");
    lcd.setCursor(0, 1);
    lcd.print("found");
    return;
  }

  lcd.setCursor(0, 0);
  if (statusChar == 'O') {
    lcd.print("Status: OBST");
  } else if (statusChar == 'C') {
    lcd.print("Status: CLEAR");
  } else {
    lcd.print("Status: ?");
  }

  lcd.setCursor(0, 1);
  lcd.print("I:");
  if (infra) {
    lcd.print("BLOCK ");
  } else {
    lcd.print("OK    ");
  }

  lcd.print(" P:");
  if (machineOn) {
    lcd.print("ON ");
  } else {
    lcd.print("OFF");
  }
}

void buzzerHandler(char statusChar) {
  if (statusChar == 'G') {
    tone(BUZZER_PIN, 500);   
    digitalWrite(LED_PINS[0], HIGH);
    digitalWrite(LED_PINS[1], HIGH);
    digitalWrite(LED_PINS[2], HIGH);
  } else {
    noTone(BUZZER_PIN);
  }
}

void ledHandler(char statusChar) {
  digitalWrite(LED_PINS[0], LOW);
  digitalWrite(LED_PINS[1], LOW);
  digitalWrite(LED_PINS[2], LOW);
  (void)statusChar;
}

void updateStableStatus() {
  if (rawStatus3 == lastRawStatus3) {
    sameRawCount3++;
  } else {
    sameRawCount3 = 1;
    lastRawStatus3 = rawStatus3;
  }

  if (sameRawCount3 >= 2) {
    stableStatus3 = rawStatus3;
  }
}

void driveStateMachine(unsigned long now) {
  char cmdToSend = 'G';  // default to stop

  if (!machineOn) {
    cmdToSend = 'G';
    sendByte(SENSOR_SLAVE_ADDR2, cmdToSend);
    return;
  }

  if (stableStatus3 == 'G') {
    moveMode  = MOVE_NORMAL;
    cmdToSend = 'G';
    sendByte(SENSOR_SLAVE_ADDR2, cmdToSend);
    return;
  }

  switch (moveMode) {
    case MOVE_NORMAL:
      if (stableStatus3 == 'O') {
        moveMode    = MOVE_OBS_STOP;
        moveStartMs = now;
        cmdToSend   = 'G';
      } else if (infraBlocked) {
        moveMode    = MOVE_BORDER_BACK;
        moveStartMs = now;
        cmdToSend   = 'R';   // reverse
      } else {
        cmdToSend   = 'C';   // forward
      }
      break;

    case MOVE_OBS_STOP:
      if (now - moveStartMs < OBST_STOP_MS) {
        cmdToSend = 'G';    // hold stop
      } else {
        moveMode    = MOVE_OBS_BACK;
        moveStartMs = now;
        cmdToSend   = 'R';  // reverse
      }
      break;

    case MOVE_OBS_BACK:
      if (now - moveStartMs < OBST_BACK_MS) {
        cmdToSend = 'R';
      } else {
        moveMode    = MOVE_OBS_TURN;
        moveStartMs = now;
        cmdToSend   = 'B';  // 45° right turn
      }
      break;

    case MOVE_OBS_TURN:
      if (now - moveStartMs < OBST_TURN_MS) {
        cmdToSend = 'B';
      } else {
        moveMode  = MOVE_NORMAL;
        cmdToSend = 'C';    // resume forward
      }
      break;

    case MOVE_BORDER_BACK:   
      if (now - moveStartMs < BORDER_BACK_MS) {
        cmdToSend = 'R';   
      } else {
        moveMode    = MOVE_BORDER_TURN;
        moveStartMs = now;
        cmdToSend   = 'O';  
      }
      break;

    case MOVE_BORDER_TURN:
      if (now - moveStartMs < BORDER_TURN_MS) {
        cmdToSend = 'O';    
      } else {
        moveMode  = MOVE_NORMAL;
        cmdToSend = 'C';
      }
      break;
  }

  sendByte(SENSOR_SLAVE_ADDR2, cmdToSend);
}

void setup() {
  Wire.begin();

  Serial.begin(9600);
  Serial.println("Master starting...");

  lcd.begin(16, 2);
  lcd.clear();
  lcd.print("Master init...");

  pinMode(BUZZER_PIN, OUTPUT);
  for (int i = 0; i < 3; i++) {
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);
  }

  stableStatus3  = 'C';
  lastRawStatus3 = 'C';
}

void loop() {
  unsigned long now = millis();

  if (now - lastHeartbeatMs >= HEARTBEAT_INTERVAL) {
    lastHeartbeatMs = now;
    Serial.print("Loop alive, ms = ");
    Serial.println(now);
  }

  if (now - lastPollMs >= POLL_INTERVAL_MS) {
    lastPollMs = now;

    Serial.println("=== POLL TICK ===");

    int r1 = requestOneByte(SENSOR_SLAVE_ADDR1);
    if (r1 >= 0) {
      lastIRRaw = r1;

      Serial.print("From 0x08 (IR): RAW=");
      Serial.print(r1);
      Serial.print("  Meaning: ");
      if (r1 == 1) Serial.println("TAPE DETECTED (blocked)");
      else         Serial.println("CLEAR");

      infraBlocked = (r1 == 1);

      Serial.print("infraBlocked = ");
      Serial.println(infraBlocked ? "true" : "false");
    } else {
      Serial.println("No valid byte from 0x08");
    }

    int r3 = requestOneByte(SENSOR_SLAVE_ADDR3);
    if (r3 >= 0) {
      rawStatus3 = (char)r3;

      Serial.print("From 0x0A (RGB/US): RAW=");
      Serial.print(r3);
      Serial.print(" -> '");
      Serial.write(rawStatus3);
      Serial.println("'");
    } else {
      Serial.println("No valid byte from 0x0A");
    }

    // Update stabilized status
    updateStableStatus();
    Serial.print("stableStatus3 = '");
    Serial.write(stableStatus3);
    Serial.println("'");

    machineOn = updateMachineOnFrom09(machineOn);

    lcdHandler(stableStatus3, infraBlocked, machineOn);
    buzzerHandler(stableStatus3);
    ledHandler(stableStatus3);

    driveStateMachine(now);

    if (!machineOn) {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("System OFF");
    }
  }
}
