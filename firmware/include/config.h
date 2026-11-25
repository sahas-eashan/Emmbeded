#pragma once
#include <stdint.h>
// Tunable values. Everything marked CALIBRATE should be checked on real hardware
// (the `hwtest` build, key 'c', shows the crow detector live).

// ---- Which sensor confirms after the PIR wakes the system ----
enum class Confirm { MIC, RADAR, MIC_AND_RADAR };
constexpr bool     USE_RADAR          = false;          // radar plugged in but NOT powered (power budget)
constexpr Confirm  CONFIRM_MODE       = Confirm::MIC;   // switch to RADAR / MIC_AND_RADAR when USE_RADAR = true
constexpr uint32_t RADAR_SETTLE_MS    = 5000;           // RCWL-0516 output is unreliable right after power-on
constexpr uint32_t RADAR_HOLD_MS      = 2000;           // a radar hit counts as "recent" for this long

// ---- Timing ----
constexpr uint32_t WARMUP_MS          = 60000;  // PIR warm-up after power-on, outputs off
constexpr uint32_t AUDIO_BLOCK_MS     = 50;     // one microphone block
constexpr uint32_t LISTEN_WINDOW_MS   = 8000;   // listen this long after the last PIR activity
constexpr uint32_t LISTEN_MAX_MS      = 20000;  // hard cap on one listen session
constexpr uint32_t BURST_MAX_MS       = 3000;   // deterrent burst limit
constexpr uint32_t COOLDOWN_MS        = 15000;  // after a burst / after battery recovery

// ---- Sleep ----
constexpr bool     ENABLE_LIGHT_SLEEP = true;   // false = stay awake and poll the PIR (debugging)

// ---- Battery ----
constexpr bool     BATTERY_MONITOR    = true;   // set false when powering the board from USB / Pi 5 V (BAT_P ~0 V)
constexpr uint32_t BATT_CHECK_PERIOD_MS = 15UL * 60UL * 1000UL;  // every 15 min (also the sleep timer wake)
constexpr float R_BATT_TOP_KOHM    = 100.0f;  // R10 (BAT_P -> GPIO35)   CALIBRATE from your BOM
constexpr float R_BATT_BOTTOM_KOHM = 27.0f;   // R11 (GPIO35 -> GND)     CALIBRATE from your BOM
constexpr float BATT_LOW_V         = 7.0f;    // 7805 needs ~7 V in
constexpr float BATT_RECOVER_V     = 7.4f;    // must be > BATT_LOW_V (hysteresis)
constexpr float BATT_INVALID_LOW_V = 3.0f;    // below this = reading is invalid
constexpr float BATT_INVALID_HIGH_V= 14.0f;   // above this = reading is invalid

// ---- Microphone ----
constexpr uint32_t MIC_SAMPLE_RATE  = 16000;
constexpr int      MIC_SLOT         = 0;      // preferred slot; micResume() switches if only the other slot has data
                                              // (slot order differs between ESP32 core 2.x and 3.x)
constexpr float    CLIP_FRACTION_MAX= 0.05f;  // more clipping than this = invalid block
constexpr uint32_t MIC_WAKE_DISCARD_MS = 300; // INMP441 needs 2^18 SCK cycles (~260 ms at 1.024 MHz) after clock start
constexpr uint32_t MIC_WAKE_TIMEOUT_MS = 800; // no valid block by then = mic fault
constexpr uint32_t MIC_STALE_MS     = 500;    // no valid block for this long while listening = mic fault

// ---- Crow-call detector (lenient demo settings; CALIBRATE for the field) ----
// A block is "active" when the 0.5-2.5 kHz band is loud enough above the learned
// background AND holds enough of the block's energy. Active blocks form a "call";
// a call of plausible length counts. Enough calls inside the window = crow.
constexpr float    CROW_BAND_LOW_HZ     = 500.0f;
constexpr float    CROW_BAND_HIGH_HZ    = 2500.0f;
constexpr float    CROW_ABOVE_FLOOR_DB  = 6.0f;    // field: 12  (lower = more sensitive)
constexpr float    CROW_MIN_BAND_DBFS   = -70.0f;  // absolute floor, ignores near-silence
constexpr float    CROW_BAND_RATIO_MIN  = 0.25f;   // field: 0.6
constexpr uint32_t CROW_CALL_MIN_MS     = 100;     // field: 150  (shorter = click / clap)
constexpr uint32_t CROW_CALL_MAX_MS     = 1500;    // field: 600  (longer = engine / wind)
constexpr uint8_t  CROW_GAP_BLOCKS      = 2;       // field: 1    quiet blocks tolerated inside one call (joins fragments)
constexpr uint8_t  CROW_CALLS_REQUIRED  = 1;       // field: 2
constexpr uint32_t CROW_WINDOW_MS       = 5000;    // calls must fall inside this window
constexpr uint8_t  CROW_RELEARN_BLOCKS  = 6;       // after wake: only update background for 300 ms
constexpr bool     CROW_LOG_BLOCKS      = false;   // true = print every block (tuning)

// ---- Audio ----
constexpr uint8_t  DF_VOLUME        = 15;     // 0..30. Two 0.5 W speakers on the PAM8403: the amp can deliver
                                              // ~1.5 W each, so stay where the sound is still clean (find it with hwtest 'd' and +/-)
constexpr uint16_t DF_TRACK         = 1;      // first MP3 on the card (root 0001.mp3)

// ---- Watchdog ----
constexpr uint32_t WDT_TIMEOUT_S    = 8;
