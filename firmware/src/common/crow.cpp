#include "crow.h"
#include "config.h"

static float floorDb = 0;
static bool floorKnown = false;
static uint8_t relearn = 0;

static bool inCall = false;
static bool longNoise = false;   // a sound ran past CROW_CALL_MAX_MS and is still going
static uint16_t callActive = 0, callGap = 0;
static float callPeakDb = -120;

static constexpr uint8_t MAX_CALLS = 8;
static uint32_t callTimes[MAX_CALLS];
static uint8_t callCount = 0;

void crowReset() {
  inCall = longNoise = false;
  callActive = callGap = 0;
  callCount = 0;
}

void crowResumed() {
  crowReset();
  relearn = CROW_RELEARN_BLOCKS;
}

float crowNoiseFloorDb() { return floorKnown ? floorDb : -120; }

static void learnFloor(float bandDb) {
  if (!floorKnown) { floorDb = bandDb; floorKnown = true; return; }
  // Quiet moments pull the floor down quickly; louder background raises it slowly (~2.5 s).
  float k = bandDb < floorDb ? 0.3f : 0.02f;
  floorDb += (bandDb - floorDb) * k;
  if (floorDb < -100) floorDb = -100;
}

static void dropOldCalls(uint32_t now) {
  uint8_t n = 0;
  for (uint8_t i = 0; i < callCount; i++)
    if (now - callTimes[i] <= CROW_WINDOW_MS) callTimes[n++] = callTimes[i];
  callCount = n;
}

// A call just ended: judge its length.
static CrowResult endCall(uint32_t now) {
  uint32_t durMs = callActive * AUDIO_BLOCK_MS;
  inCall = false;
  callActive = callGap = 0;
  if (durMs < CROW_CALL_MIN_MS) {
    Serial.printf("[%8u]   sound %u ms - too short (click/clap?), ignored\n", now, durMs);
    return CrowResult::NONE;
  }
  dropOldCalls(now);
  if (callCount < MAX_CALLS) callTimes[callCount++] = now;
  Serial.printf("[%8u]   CROW-LIKE CALL %u ms, peak %.1f dB (background %.1f) -> %u/%u in %u s\n", now, durMs,
                callPeakDb, floorDb, callCount, CROW_CALLS_REQUIRED, CROW_WINDOW_MS / 1000);
  if (callCount >= CROW_CALLS_REQUIRED) {
    callCount = 0;
    return CrowResult::CONFIRMED;
  }
  return CrowResult::CALL;
}

void crowLearn(const MicFeatures &m) {
  if (m.valid) learnFloor(m.bandDbfs);
}

CrowResult crowUpdate(const MicFeatures &m, uint32_t now) {
  if (!m.valid) return CrowResult::NONE;

  if (relearn) {  // just woke: background only, no detection
    relearn--;
    learnFloor(m.bandDbfs);
    return CrowResult::NONE;
  }

  bool active = floorKnown && m.bandDbfs >= floorDb + CROW_ABOVE_FLOOR_DB && m.bandDbfs >= CROW_MIN_BAND_DBFS &&
                m.bandRatio >= CROW_BAND_RATIO_MIN;

  if (CROW_LOG_BLOCKS)
    Serial.printf("[%8u] band %6.1f dB  floor %6.1f  ratio %.2f  full %6.1f %s\n", now, m.bandDbfs, floorDb,
                  m.bandRatio, m.rmsDbfs, active ? "ACTIVE" : "");

  if (active) {
    if (longNoise) {  // continuous sound (engine, wind): absorb it into the background
      floorDb += (m.bandDbfs - floorDb) * 0.1f;
      return CrowResult::NONE;
    }
    if (!inCall) { inCall = true; callActive = 0; callPeakDb = -120; }
    callActive++;
    callGap = 0;
    if (m.bandDbfs > callPeakDb) callPeakDb = m.bandDbfs;
    if (callActive * AUDIO_BLOCK_MS > CROW_CALL_MAX_MS) {
      Serial.printf("[%8u]   continuous sound > %u ms (engine/wind?), ignored\n", now, CROW_CALL_MAX_MS);
      inCall = false;
      callActive = callGap = 0;
      longNoise = true;
    }
    return CrowResult::NONE;
  }
  longNoise = false;

  if (inCall) {
    if (++callGap <= CROW_GAP_BLOCKS) return CrowResult::NONE;  // short dip inside one call
    return endCall(now);
  }

  learnFloor(m.bandDbfs);  // only learn the background between calls
  return CrowResult::NONE;
}
