#pragma once
#include <Arduino.h>

// RCWL-0516 behind the Q3 -> Q2 high-side switch (GPIO16 HIGH = powered).
// With USE_RADAR = false every call keeps the radar unpowered and reports no motion,
// so the confirm logic can stay the same while the radar is left plugged in but off.
void radarBegin();         // switch OFF, configure pins (call first thing in setup)
void radarOn();            // power on + start the settle timer (no-op when USE_RADAR = false)
void radarOff();           // power off (always allowed)
bool radarIsOn();
bool radarReady();         // powered and settled for RADAR_SETTLE_MS
bool radarMotion();        // ready AND output HIGH right now
