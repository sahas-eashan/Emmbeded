#include "radar.h"
#include "config.h"
#include "pins.h"

static bool powered = false;
static uint32_t onSince = 0;

void radarBegin() {
  digitalWrite(PIN_RADAR_POWER, LOW);  // set the level before enabling the output
  pinMode(PIN_RADAR_POWER, OUTPUT);
  pinMode(PIN_RADAR_OUT, INPUT);       // R4 pull-down keeps it LOW while the radar is unpowered
  powered = false;
}

void radarOn() {
  if (!USE_RADAR || powered) return;
  digitalWrite(PIN_RADAR_POWER, HIGH);
  powered = true;
  onSince = millis();
  Serial.printf("[%8u] radar power ON, settling %u s\n", onSince, RADAR_SETTLE_MS / 1000);
}

void radarOff() {
  digitalWrite(PIN_RADAR_POWER, LOW);
  if (powered) Serial.printf("[%8u] radar power OFF\n", (uint32_t)millis());
  powered = false;
}

bool radarIsOn() { return powered; }

bool radarReady() { return powered && millis() - onSince >= RADAR_SETTLE_MS; }

bool radarMotion() { return radarReady() && digitalRead(PIN_RADAR_OUT) == HIGH; }
