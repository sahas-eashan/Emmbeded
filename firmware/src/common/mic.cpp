#include "mic.h"
#include <driver/i2s.h>
#include <math.h>
#include "config.h"
#include "pins.h"

static constexpr i2s_port_t PORT = I2S_NUM_0;
static constexpr size_t FRAMES = MIC_SAMPLE_RATE * AUDIO_BLOCK_MS / 1000;  // 800
static int32_t buf[FRAMES * 2];
static bool installed = false;
static int activeSlot = MIC_SLOT;

int micSlot() { return activeSlot; }

// Power ratio -> dB, with silence clamped to -120 dB (avoids -900 dB from denormal filter tails).
static float toDb(double power) { return power > 1e-12 ? (float)(10.0 * log10(power)) : -120.0f; }

// ---------- 2nd-order IIR (RBJ cookbook), transposed direct form II ----------
struct Biquad {
  float b0 = 1, b1 = 0, b2 = 0, a1 = 0, a2 = 0, z1 = 0, z2 = 0;
  void set(bool highpass, float f0, float fs, float q = 0.7071f) {
    float w = 2.0f * (float)M_PI * f0 / fs, c = cosf(w), alpha = sinf(w) / (2.0f * q), a0 = 1.0f + alpha;
    if (highpass) { b0 = (1 + c) / 2; b1 = -(1 + c); b2 = (1 + c) / 2; }
    else          { b0 = (1 - c) / 2; b1 = 1 - c;    b2 = (1 - c) / 2; }
    b0 /= a0; b1 /= a0; b2 /= a0; a1 = -2.0f * c / a0; a2 = (1.0f - alpha) / a0;
    z1 = z2 = 0;
  }
  inline float run(float x) {
    float y = b0 * x + z1;
    z1 = b1 * x - a1 * y + z2;
    z2 = b2 * x - a2 * y;
    return y;
  }
  void reset() { z1 = z2 = 0; }
};
// Band-pass = high-pass at CROW_BAND_LOW_HZ followed by low-pass at CROW_BAND_HIGH_HZ, per slot.
static Biquad hp[2], lp[2];

static void resetFilters() {
  for (int s = 0; s < 2; s++) { hp[s].reset(); lp[s].reset(); }
}

bool micBegin() {
  i2s_config_t cfg = {};
  cfg.mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX);
  cfg.sample_rate = MIC_SAMPLE_RATE;
  cfg.bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT;
  cfg.channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT;
  cfg.communication_format = I2S_COMM_FORMAT_STAND_I2S;
  cfg.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1;
  cfg.dma_buf_count = 6;
  cfg.dma_buf_len = 256;
  cfg.use_apll = false;

  i2s_pin_config_t pins = {};
  pins.mck_io_num = I2S_PIN_NO_CHANGE;
  pins.bck_io_num = PIN_MIC_SCK;
  pins.ws_io_num = PIN_MIC_WS;
  pins.data_out_num = I2S_PIN_NO_CHANGE;
  pins.data_in_num = PIN_MIC_SD;

  if (i2s_driver_install(PORT, &cfg, 0, nullptr) != ESP_OK) return false;
  if (i2s_set_pin(PORT, &pins) != ESP_OK) { i2s_driver_uninstall(PORT); return false; }
  for (int s = 0; s < 2; s++) {
    hp[s].set(true, CROW_BAND_LOW_HZ, MIC_SAMPLE_RATE);
    lp[s].set(false, CROW_BAND_HIGH_HZ, MIC_SAMPLE_RATE);
  }
  installed = true;
  return true;  // driver running; call micResume() to wait for valid data
}

void micPause() {
  if (installed) i2s_stop(PORT);  // SCK stops -> INMP441 powers itself down
}

bool micResume() {
  if (!installed) return false;
  i2s_start(PORT);
  i2s_zero_dma_buffer(PORT);
  resetFilters();
  uint32_t t0 = millis();
  MicFeatures f[2];
  while (millis() - t0 < MIC_WAKE_TIMEOUT_MS) {
    bool ok = micReadBlock(f, 200);
    if (millis() - t0 < MIC_WAKE_DISCARD_MS) continue;  // mic still starting up: throw away
    if (!ok) continue;
    if (f[activeSlot].valid) return true;
    if (f[1 - activeSlot].valid) {  // slot order differs between ESP32 core versions: follow the data
      activeSlot = 1 - activeSlot;
      Serial.printf("mic: data is in slot %d - using that slot\n", activeSlot);
      return true;
    }
  }
  return false;
}

static void features(int slot, size_t frames, MicFeatures &f) {
  // INMP441: 24-bit left-justified in 32-bit slot.
  double mean = 0;
  for (size_t i = 0; i < frames; i++) mean += (buf[i * 2 + slot] >> 8);
  mean /= frames;

  const float FS = 8388608.0f;  // 2^23
  double full = 0, band = 0;
  uint32_t zc = 0, clip = 0;
  bool prevNeg = false, allSame = true;
  int32_t first = buf[slot];
  for (size_t i = 0; i < frames; i++) {
    int32_t raw = buf[i * 2 + slot];
    if (raw != first) allSame = false;
    int32_t v = raw >> 8;
    if (abs(v) > 0.98f * FS) clip++;
    float x = (float)(v - mean) / FS;          // -1..1, DC removed
    full += (double)x * x;
    float y = lp[slot].run(hp[slot].run(x));   // crow band
    band += (double)y * y;
    bool neg = x < 0;
    if (i && neg != prevNeg) zc++;
    prevNeg = neg;
  }
  f.rmsDbfs = toDb(full / frames);
  f.bandDbfs = toDb(band / frames);
  f.bandRatio = full > 1e-12 * frames ? (float)fmin(1.0, band / full) : 0;
  f.zcr = (float)zc / frames;
  f.clipFrac = (float)clip / frames;
  f.valid = !allSame && f.clipFrac <= CLIP_FRACTION_MAX;
}

bool micReadBlock(MicFeatures out[2], uint32_t timeoutMs) {
  out[0] = MicFeatures(); out[1] = MicFeatures();
  if (!installed) return false;
  size_t got = 0;
  if (i2s_read(PORT, buf, sizeof(buf), &got, pdMS_TO_TICKS(timeoutMs)) != ESP_OK) return false;
  size_t frames = got / (2 * sizeof(int32_t));
  if (frames < FRAMES / 2) return false;
  features(0, frames, out[0]);
  features(1, frames, out[1]);
  return true;
}
