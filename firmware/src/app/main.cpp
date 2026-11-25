// Bird Repellent System - final firmware.
//
//   Power on -> outputs off -> self-check -> WARMUP (60 s: PIR settles, mic learns the background)
//   IDLE     : light sleep; wake on PIR HIGH, or the 15-min battery-check timer
//   LISTEN   : PIR woke us -> mic (+ radar when USE_RADAR) confirms a crow;
//              window LISTEN_WINDOW_MS after the last PIR activity, at most LISTEN_MAX_MS
//   DETER    : DFPlayer plays, max BURST_MAX_MS
//   COOLDOWN : COOLDOWN_MS, detections ignored; then LISTEN if PIR still active, else IDLE
//   BATT_LOW : outputs + radar off, timer-only sleep, re-check every 15 min, recover above BATT_RECOVER_V
//   Audio fault (DFPlayer missing / error): crows are still detected and logged, no sound until restart.
//   Mic fault (no valid data): logged, back to IDLE, retried on the next wake.
//   ISR: only records that the PIR fired; all decisions happen in loop().
#include <Arduino.h>
#include <DFRobotDFPlayerMini.h>
#include <driver/gpio.h>
#include <esp_sleep.h>
#include <esp_task_wdt.h>
#include "battery.h"
#include "config.h"
#include "crow.h"
#include "mic.h"
#include "pins.h"
#include "radar.h"

static_assert(USE_RADAR || CONFIRM_MODE == Confirm::MIC, "CONFIRM_MODE uses the radar but USE_RADAR is false");
static_assert(BATT_RECOVER_V > BATT_LOW_V, "battery hysteresis needs BATT_RECOVER_V > BATT_LOW_V");

enum class State { WARMUP, IDLE, LISTEN, DETER, COOLDOWN, BATT_LOW };

static const char *stateName(State s) {
  switch (s) {
    case State::WARMUP: return "WARMUP";
    case State::IDLE: return "IDLE";
    case State::LISTEN: return "LISTEN";
    case State::DETER: return "DETER";
    case State::COOLDOWN: return "COOLDOWN";
    case State::BATT_LOW: return "BATT_LOW";
  }
  return "?";
}

// ---------- ISR: record the event, nothing else ----------
static volatile bool pirEvent = false;
static void IRAM_ATTR onPirIsr() { pirEvent = true; }

// ---------- globals ----------
static DFRobotDFPlayerMini df;
static bool audioOk = false;
static bool micAwake = false;
static State state = State::WARMUP;
static uint32_t stateSince = 0, bootMs = 0;
static uint32_t listenStart = 0, lastPirMs = 0, lastRadarHitMs = 0;
static uint32_t lastValidMicMs = 0, lastBattCheckMs = 0;

static void setState(State s) {
  if (s == state) return;
  Serial.printf("[%8u] %s -> %s\n", (uint32_t)millis(), stateName(state), stateName(s));
  state = s;
  stateSince = millis();
}

static bool pirActive(uint32_t now) {
  return digitalRead(PIN_PIR_OUT) == HIGH || (lastPirMs && now - lastPirMs < 300);
}

// ---------- audio ----------
static bool audioBegin() {
  Serial2.begin(9600, SERIAL_8N1, PIN_DF_RX, PIN_DF_TX);
  if (!df.begin(Serial2, true, true)) return false;
  df.volume(DF_VOLUME);
  df.stop();
  return true;
}

static void outputsOff() {
  if (audioOk) df.stop();
}

static void pollDfErrors() {
  if (!audioOk || !df.available()) return;
  uint8_t t = df.readType();
  int v = df.read();
  if (t == DFPlayerError || t == DFPlayerCardRemoved) {
    audioOk = false;
    Serial.printf("[%8u] AUDIO FAULT: DFPlayer error type %u value %d - sound off until restart\n", (uint32_t)millis(), t, v);
  }
}

// ---------- battery: every BATT_CHECK_PERIOD_MS (15 min) ----------
static void checkBattery(uint32_t now) {
  lastBattCheckMs = now;
  if (!BATTERY_MONITOR) return;
  float v = batteryVolts();
  bool invalid = v < BATT_INVALID_LOW_V || v > BATT_INVALID_HIGH_V;
  Serial.printf("[%8u] battery %.2f V%s\n", now, v, invalid ? " (invalid reading)" : "");

  if (state == State::BATT_LOW) {
    if (!invalid && v >= BATT_RECOVER_V) {
      Serial.printf("[%8u] battery recovered -> cooldown before re-arming\n", now);
      setState(State::COOLDOWN);
    }
  } else if (invalid || v < BATT_LOW_V) {
    outputsOff();
    radarOff();
    Serial.printf("[%8u] BATTERY %s - outputs off, checking again every %u min\n", now,
                  invalid ? "READING INVALID" : "LOW", BATT_CHECK_PERIOD_MS / 60000);
    setState(State::BATT_LOW);
  }
}

// ---------- microphone wake (INMP441 needs ~260 ms after its clock restarts) ----------
static void wakeMic() {
  if (micAwake) return;
  bool ok = micResume();
  micAwake = true;
  crowResumed();
  lastValidMicMs = millis();
  if (!ok) Serial.printf("[%8u] mic: no valid data after wake (check J1 wiring)\n", (uint32_t)millis());
}

// ---------- light sleep ----------
// Returns the wake cause. pirWake = false -> timer only (battery low).
static esp_sleep_wakeup_cause_t lightSleep(bool pirWake) {
  uint32_t now = millis();
  uint32_t sinceCheck = now - lastBattCheckMs;
  uint32_t timerMs = sinceCheck >= BATT_CHECK_PERIOD_MS ? 1000 : BATT_CHECK_PERIOD_MS - sinceCheck;

  outputsOff();
  radarOff();
  Serial.printf("[%8u] light sleep (%s), battery check in %u s\n", now,
                pirWake ? "wake on PIR" : "battery low, timer only", timerMs / 1000);
  Serial.flush();
  Serial2.flush();
  micPause();  // clocks stop -> INMP441 powers down
  micAwake = false;
  detachInterrupt(digitalPinToInterrupt(PIN_PIR_OUT));

  esp_sleep_enable_timer_wakeup((uint64_t)timerMs * 1000ULL);
  if (pirWake) {
    gpio_wakeup_enable((gpio_num_t)PIN_PIR_OUT, GPIO_INTR_HIGH_LEVEL);
    esp_sleep_enable_gpio_wakeup();
  }

  esp_sleep_wakeup_cause_t cause;
  if (pirWake && digitalRead(PIN_PIR_OUT) == HIGH) {
    cause = ESP_SLEEP_WAKEUP_GPIO;  // PIR already active: don't sleep at all
  } else {
    esp_task_wdt_delete(NULL);
    esp_light_sleep_start();
    esp_task_wdt_add(NULL);
    cause = esp_sleep_get_wakeup_cause();
  }

  if (pirWake) gpio_wakeup_disable((gpio_num_t)PIN_PIR_OUT);
  esp_sleep_disable_wakeup_source(ESP_SLEEP_WAKEUP_ALL);
  pirEvent = false;
  attachInterrupt(digitalPinToInterrupt(PIN_PIR_OUT), onPirIsr, RISING);
  return cause;
}

// ---------- transitions ----------
static void startListen() {
  radarOn();   // no-op while USE_RADAR = false
  wakeMic();
  crowReset();
  uint32_t now = millis();
  listenStart = lastPirMs = now;
  lastRadarHitMs = 0;
  Serial.printf("[%8u] PIR -> listening for crows (%s)\n", now,
                CONFIRM_MODE == Confirm::MIC ? "mic" : CONFIRM_MODE == Confirm::RADAR ? "radar" : "mic + radar");
  setState(State::LISTEN);
}

static void startDeterrent(uint32_t now) {
  if (!audioOk) {
    Serial.printf("[%8u] CROW CONFIRMED - but audio is off (fault), no sound\n", now);
    setState(State::COOLDOWN);
    return;
  }
  Serial.printf("[%8u] CROW CONFIRMED -> deterrent sound (max %u s)\n", now, BURST_MAX_MS / 1000);
  df.play(DF_TRACK);
  setState(State::DETER);
}

// ---------- setup / loop ----------
void setup() {
  radarBegin();  // radar switch OFF before anything else (R16 also holds it off during reset)
  pinMode(PIN_PIR_OUT, INPUT);
  pinMode(PIN_BOOT_BTN, INPUT);

  Serial.begin(115200);
  delay(200);
  Serial.println(F("\n== Bird Repellent System - main firmware =="));
  Serial.printf("Confirm: %s | radar %s | battery check every %u min%s | sleep %s\n",
                CONFIRM_MODE == Confirm::MIC ? "MIC" : CONFIRM_MODE == Confirm::RADAR ? "RADAR" : "MIC+RADAR",
                USE_RADAR ? "enabled" : "disabled (unpowered)", BATT_CHECK_PERIOD_MS / 60000,
                BATTERY_MONITOR ? "" : " (monitor OFF)", ENABLE_LIGHT_SLEEP ? "on" : "off");
  bootMs = millis();

  batteryBegin();
  if (!micBegin()) {
    Serial.println(F("Setup failed (microphone I2S driver) - restarting in 5 s"));
    delay(5000);
    ESP.restart();
  }
  bool micOk = micResume();
  micAwake = true;
  lastValidMicMs = millis();
  audioOk = audioBegin();
  Serial.printf("Setup: mic %s, DFPlayer %s\n", micOk ? "OK" : "NO VALID DATA (check J1)",
                audioOk ? "OK" : "FAIL (sound disabled until restart)");

  esp_task_wdt_init(WDT_TIMEOUT_S, true);
  esp_task_wdt_add(NULL);
  attachInterrupt(digitalPinToInterrupt(PIN_PIR_OUT), onPirIsr, RISING);

  stateSince = millis();
  checkBattery(millis());
  if (state == State::WARMUP) Serial.printf("Warm-up %u s, outputs off\n", WARMUP_MS / 1000);
}

void loop() {
  // 1) Microphone: one 50 ms block while awake (this read also paces the loop).
  MicFeatures f[2];
  bool haveBlock = false;
  if (micAwake) {
    if (micReadBlock(f) && f[micSlot()].valid) { haveBlock = true; lastValidMicMs = millis(); }
  } else {
    delay(20);
  }
  const MicFeatures &m = f[micSlot()];
  uint32_t now = millis();

  // 2) PIR: event recorded by the ISR, or the level is still HIGH.
  if (pirEvent) { pirEvent = false; lastPirMs = now; }
  if (digitalRead(PIN_PIR_OUT) == HIGH) lastPirMs = now;

  // 3) Battery every 15 min, DFPlayer errors every pass.
  if (now - lastBattCheckMs >= BATT_CHECK_PERIOD_MS) checkBattery(now);
  pollDfErrors();

  // 4) State machine (elapsed-time deadlines, never blocking waits).
  switch (state) {
    case State::WARMUP:
      if (haveBlock) crowLearn(m);  // learn the background while the PIR settles
      if (now - bootMs >= WARMUP_MS) setState(State::IDLE);
      break;

    case State::IDLE:
      if (pirActive(now)) {
        startListen();
      } else if (ENABLE_LIGHT_SLEEP) {
        esp_sleep_wakeup_cause_t cause = lightSleep(true);
        uint32_t t = millis();
        if (cause == ESP_SLEEP_WAKEUP_GPIO) {
          Serial.printf("[%8u] woke: PIR\n", t);
          startListen();
        } else {
          Serial.printf("[%8u] woke: battery timer\n", t);
          checkBattery(t);  // stays IDLE -> sleeps again on the next pass
        }
      }
      break;

    case State::LISTEN: {
      if (now - lastValidMicMs > MIC_STALE_MS) {
        Serial.printf("[%8u] MIC FAULT: no valid data for %u ms - back to idle\n", now, MIC_STALE_MS);
        radarOff();
        setState(State::IDLE);
        break;
      }
      bool crow = haveBlock && crowUpdate(m, now) == CrowResult::CONFIRMED;
      if (radarMotion()) lastRadarHitMs = now;
      bool radarRecent = lastRadarHitMs && now - lastRadarHitMs <= RADAR_HOLD_MS;

      bool confirmed = false;
      switch (CONFIRM_MODE) {
        case Confirm::MIC: confirmed = crow; break;
        case Confirm::RADAR: confirmed = radarRecent; break;
        case Confirm::MIC_AND_RADAR: confirmed = crow && radarRecent; break;
      }

      uint32_t windowEnd = lastPirMs + LISTEN_WINDOW_MS;
      uint32_t hardEnd = listenStart + LISTEN_MAX_MS;
      if (confirmed) {
        startDeterrent(now);
      } else if ((int32_t)(now - windowEnd) >= 0 || (int32_t)(now - hardEnd) >= 0) {
        Serial.printf("[%8u] listen window over - no crow confirmed\n", now);
        radarOff();
        setState(State::IDLE);
      }
      break;
    }

    case State::DETER:
      if (now - stateSince >= BURST_MAX_MS) {
        outputsOff();
        setState(State::COOLDOWN);
      }
      break;

    case State::COOLDOWN:  // mic keeps running but is not evaluated (it would hear our own speaker)
      if (now - stateSince >= COOLDOWN_MS) {
        if (pirActive(now)) startListen();
        else { radarOff(); setState(State::IDLE); }
      }
      break;

    case State::BATT_LOW:
      if (ENABLE_LIGHT_SLEEP) {
        lightSleep(false);
        checkBattery(millis());
      }
      break;
  }

  // 5) Feed the watchdog only after a full pass of useful work.
  esp_task_wdt_reset();
}
