#include <Arduino.h>
// ===== Sensor test 1: PIR HC-SR501 =====
// Upload:  pio run -e pir -t upload --upload-port COM3      Monitor: pio device monitor -p COM3 -b 115200
// Wiring (from the PCB): header U2  pin1 = GND, pin2 = OUT -> GPIO34 (via R8, R9 pull-down), pin3 = 3V3
//
// What to expect:
//   - First 60 s: warm-up. The PIR may toggle randomly; ignore it.
//   - Then: stand still / leave the room -> stays LOW.
//           wave a hand 1-2 m in front   -> goes HIGH, stays HIGH for the
//           HC-SR501 "time" pot setting (min ~3 s), then LOW.
//   - Every 5 s a status line shows the current level and trigger count.

const int PIN_PIR = 34;          // input-only pin, no internal pull-up/down available
const uint32_t WARMUP_MS = 60000;

int lastLevel = -1;
uint32_t riseMs = 0;
uint32_t triggers = 0;
uint32_t lastStatus = 0;
bool warmupDone = false;

void setup() {
  Serial.begin(115200);
  delay(300);
  pinMode(PIN_PIR, INPUT);
  Serial.println();
  Serial.println("=== PIR test (GPIO34) ===");
  Serial.println("Warming up for 60 s - don't judge readings yet...");
}

void loop() {
  uint32_t now = millis();
  int level = digitalRead(PIN_PIR);

  if (!warmupDone && now >= WARMUP_MS) {
    warmupDone = true;
    triggers = 0;
    Serial.println(">>> Warm-up done. Stay still, then wave a hand in front of the PIR.");
  }

  if (level != lastLevel) {
    const char *tag = warmupDone ? "" : " (warm-up)";
    if (level == HIGH) {
      riseMs = now;
      if (warmupDone) triggers++;
      Serial.printf("[%6.1f s] MOTION   -> HIGH%s  #%lu\n", now / 1000.0, tag, (unsigned long)triggers);
    } else if (lastLevel == HIGH) {
      Serial.printf("[%6.1f s] clear    -> LOW%s   (was HIGH %.1f s)\n", now / 1000.0, tag, (now - riseMs) / 1000.0);
    } else {
      Serial.printf("[%6.1f s] start level LOW\n", now / 1000.0);
    }
    lastLevel = level;
  }

  if (now - lastStatus >= 5000) {
    lastStatus = now;
    Serial.printf("[%6.1f s] status: GPIO34=%d  triggers=%lu%s\n", now / 1000.0, level,
                  (unsigned long)triggers, warmupDone ? "" : "  (warming up)");
  }

  delay(10);
}
