#pragma once
#include <Arduino.h>

// INMP441 on I2S0 (legacy IDF 4.4 driver). Reads stereo so either slot works;
// L/R pin grounded normally puts the data in one slot - hwtest shows which.
// The mic has no enable pin: it powers down by itself when SCK stops (micPause)
// and needs ~2^18 SCK cycles after the clock restarts (micResume) to give valid data.
struct MicFeatures {
  bool  valid = false;     // block read OK, not stuck, not clipping
  float rmsDbfs = -120;    // full-band level, dB relative to full scale
  float bandDbfs = -120;   // level inside CROW_BAND_LOW_HZ..CROW_BAND_HIGH_HZ
  float bandRatio = 0;     // band energy / full-band energy (0..1)
  float zcr = 0;           // zero-crossing rate (fraction of samples)
  float clipFrac = 0;      // fraction of samples near full scale
};

bool micBegin();                 // install driver + wait for valid data; true on success
void micPause();                 // stop clocks -> mic powers down (before light sleep)
bool micResume();                // restart clocks, discard start-up data; true once data is valid
int  micSlot();                  // slot carrying the mic: MIC_SLOT, or the other one if only it has data
// Capture one AUDIO_BLOCK_MS block and compute features for both slots.
bool micReadBlock(MicFeatures out[2], uint32_t timeoutMs = 200);
