#pragma once
#include <Arduino.h>
#include "config.h"
#include "pins.h"

// Battery voltage at BAT_P (after reverse-polarity MOSFET Q1), via R10/R11 divider.
inline float batteryVolts() {
  uint32_t mv = 0;
  for (int i = 0; i < 16; i++) mv += analogReadMilliVolts(PIN_BATT_SENSE);  // calibrated ADC
  float vAdc = (mv / 16.0f) / 1000.0f;
  return vAdc * (R_BATT_TOP_KOHM + R_BATT_BOTTOM_KOHM) / R_BATT_BOTTOM_KOHM;
}

inline void batteryBegin() {
  analogSetPinAttenuation(PIN_BATT_SENSE, ADC_11db);  // 0..~3.1 V input range
}
