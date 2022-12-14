#include <Mouse.h>
// #include "HID-Project.h"

// IMPORTANT: The mouse may only move by a max of 127 pixels
// Singed char is between -127 to 127
const int negMax = -127;
const int posMax = 127;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(2000000);
  delay(3000);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available() > 0) {
    String data = Serial.readStringUntil('x');
    int colonPos = data.indexOf(':');

    if(!(colonPos > 0)) return;

    int dx = data.substring(0, colonPos).toInt();
    int dy = data.substring(colonPos + 1, data.length()).toInt();

    // AbsoluteMouse.moveTo(0, 0);
    moveMouseX(dx);
    moveMouseY(dy);
  }
}

void moveMouseX(int dx) {
  int spawns = int(dx/posMax);
  int remainder = int(dx%posMax);
  bool isNegative = false;

  if(dx <= negMax) {
    spawns = int(dx/negMax);
    remainder = int(dx % negMax);
    isNegative = true;
  }

  for(int i = 0; i < spawns; i++) {
    Mouse.move(isNegative ? negMax : posMax, 0, 0);
  }

  Mouse.move(remainder, 0, 0);
}

void moveMouseY(int dy) {
  int spawns = int(dy/posMax);
  int remainder = int(dy%posMax);
  bool isNegative = false;

  if(dy <= negMax) {
    spawns = int(dy/negMax);
    remainder = int(dy % negMax);
    isNegative = true;
  }

  for(int i = 0; i < spawns; i++) {
    Mouse.move(0, isNegative ? negMax : posMax, 0);
  }

  Mouse.move(0, remainder, 0);
}