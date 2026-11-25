#pragma once
#include <Arduino.h>
#include "mic.h"

// Crow-call detector, fed one microphone block (AUDIO_BLOCK_MS) at a time.
//   A: block "active"  = crow-band level >= background + CROW_ABOVE_FLOOR_DB
//                        and band holds >= CROW_BAND_RATIO_MIN of the energy
//   B: call            = run of active blocks lasting CROW_CALL_MIN_MS..CROW_CALL_MAX_MS
//   C: crow confirmed  = CROW_CALLS_REQUIRED calls inside CROW_WINDOW_MS
// The background level adapts while no call is in progress (fast down, slow up).
enum class CrowResult { NONE, CALL, CONFIRMED };

void crowReset();               // forget calls in progress (keep the learned background)
void crowResumed();             // after a wake: re-learn the background for a few blocks first
void crowLearn(const MicFeatures &m);   // background only (warm-up), never detects
CrowResult crowUpdate(const MicFeatures &m, uint32_t nowMs);
float crowNoiseFloorDb();
