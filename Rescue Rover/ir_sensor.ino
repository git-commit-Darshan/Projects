#include <Wire.h>
// Slave 0x08

#define SLAVE_ADD 0x08

const int ir_pin = A0;
int tapeDetected = 0, lastChecked;
const int threshold = 200;
const int wt = 50;a

void setup()
{
  pinMode(ir_pin, INPUT);
  Wire.begin(SLAVE_ADD);
  Wire.onRequest(inBound);
  Serial.begin(9600);
}

void loop()
{
  int ir = analogRead(ir_pin);
  Serial.println(ir);

  if(millis() - lastChecked >= wt) {
      // detected the tape
      if(ir > threshold) {
        tapeDetected = 1;
      Serial.println("detected");
      }
      else tapeDetected = 0;
    lastChecked = millis();
  }

}

void inBound() {
  Serial.println("Send");
    Wire.write(tapeDetected);
}