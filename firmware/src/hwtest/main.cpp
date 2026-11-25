// Module-by-module hardware test. Open the serial monitor at 115200 and
// type a letter + Enter. Any key stops a live test.
#include <Arduino.h>
#include <DFRobotDFPlayerMini.h>
#include "battery.h"
#include "config.h"
#include "crow.h"
#include "mic.h"
#include "pins.h"

static DFRobotDFPlayerMini df;
static bool dfOk = false;
static uint8_t volume = DF_VOLUME;
static bool radarOn = false;

// True when a real key arrives. Line endings (\r \n) from monitors that
// append them (Arduino IDE "Both NL & CR") are ignored, so they don't stop a live test.
static bool keyPressed() {
  bool key = false;
  while (Serial.available()) {
    int c = Serial.read();
    if (c > ' ') key = true;
  }
  return key;
}

static void setRadar(bool on) {
  radarOn = on;
  digitalWrite(PIN_RADAR_POWER, on ? HIGH : LOW);
  Serial.printf("Radar power %s (GPIO%d %s)\n", on ? "ON" : "OFF", PIN_RADAR_POWER, on ? "HIGH" : "LOW");
}

static void help() {
  Serial.println(F("\n===== Bird Repellent - hardware test ====="));
  Serial.printf("PIR GPIO%d | Radar out GPIO%d, power GPIO%d | Mic SCK %d WS %d SD %d\n",
                PIN_PIR_OUT, PIN_RADAR_OUT, PIN_RADAR_POWER, PIN_MIC_SCK, PIN_MIC_WS, PIN_MIC_SD);
  Serial.printf("DFPlayer TX %d -> DF RX, RX %d <- DF TX | Battery GPIO%d | BOOT GPIO%d\n",
                PIN_DF_TX, PIN_DF_RX, PIN_BATT_SENSE, PIN_BOOT_BTN);
  Serial.println(F(" b  battery voltage (5 readings)"));
  Serial.println(F(" p  PIR live, mic stopped (needs ~60 s warm-up after power-on)"));
  Serial.println(F(" P  PIR live, mic running (if only this one false-triggers: supply noise)"));
  Serial.println(F(" r  radar live (switches radar power ON)"));
  Serial.println(F(" R  toggle radar power (measure 5 V at U7 pin 1)"));
  Serial.println(F(" m  microphone live - both I2S slots, the firmware picks the live slot itself"));
  Serial.println(F(" c  crow detector live (tune CROW_* in config.h)"));
  Serial.println(F(" d  DFPlayer: init + play track 1 for 5 s"));
  Serial.println(F(" s  DFPlayer stop     + / -  volume"));
  Serial.println(F(" k  BOOT button live"));
  Serial.println(F(" a  ALL sensors live dashboard"));
  Serial.println(F(" h  this help"));
}

static void testBattery() {
  for (int i = 0; i < 5; i++) {
    uint32_t mv = analogReadMilliVolts(PIN_BATT_SENSE);
    Serial.printf("ADC pin %4u mV  ->  BAT_P %.2f V\n", mv, batteryVolts());
    delay(300);
  }
  Serial.println(F("Compare with a multimeter on BAT_P; if off, fix R_BATT_* in config.h"));
}

static void liveDigital(const char *name, int pin) {
  Serial.printf("%s live on GPIO%d - any key to stop\n", name, pin);
  int last = -1; uint32_t tRise = 0;
  while (!keyPressed()) {
    int v = digitalRead(pin);
    if (v != last) {
      if (v) { tRise = millis(); Serial.printf("[%7lu ms] %s HIGH (motion)\n", millis(), name); }
      else if (last == 1) Serial.printf("[%7lu ms] %s LOW  (held %lu ms)\n", millis(), name, millis() - tRise);
      else Serial.printf("[%7lu ms] %s LOW\n", millis(), name);
      last = v;
    }
    delay(5);
  }
}

static void testMic() {
  Serial.println(F("Mic live: slot0 / slot1 dBFS, ZCR, clip. Clap or talk - any key to stop"));
  Serial.println(F("The slot whose level jumps carries the mic. A dead slot stays at -120 or invalid."));
  while (!keyPressed()) {
    MicFeatures f[2];
    if (!micReadBlock(f)) { Serial.println(F("I2S read FAILED - check J1 wiring / 3V3")); delay(300); continue; }
    static uint32_t n = 0;
    if (++n % 4) continue;  // print every 4th block (5 lines/s)
    Serial.printf("slot0 %6.1f dB zcr %.3f clip %.3f %s | slot1 %6.1f dB zcr %.3f clip %.3f %s\n",
                  f[0].rmsDbfs, f[0].zcr, f[0].clipFrac, f[0].valid ? "ok " : "BAD",
                  f[1].rmsDbfs, f[1].zcr, f[1].clipFrac, f[1].valid ? "ok " : "BAD");
  }
}

static void dfInit() {
  Serial2.begin(9600, SERIAL_8N1, PIN_DF_RX, PIN_DF_TX);
  Serial.println(F("DFPlayer init (SD card must be inserted)..."));
  dfOk = df.begin(Serial2, true, true);
  if (!dfOk) {
    Serial.println(F("DFPlayer NOT responding. Check: P2 pin3 = DF RX, pin4 = DF TX, 5 V on P2 pin1, SD card."));
    return;
  }
  df.volume(volume);
  delay(200);
  Serial.printf("DFPlayer OK, files on card: %d\n", df.readFileCounts());
}

static void testDf() {
  if (!dfOk) dfInit();
  if (!dfOk) return;
  Serial.printf("Playing track %u at volume %u for 5 s (any key stops)\n", DF_TRACK, volume);
  df.play(DF_TRACK);
  uint32_t t0 = millis();
  while (millis() - t0 < 5000 && !keyPressed()) {
    if (df.available()) Serial.printf("DF event type %d value %d\n", df.readType(), df.read());
    delay(20);
  }
  df.stop();
  Serial.println(F("Stopped. Watch the 7805 (U4) temperature during long tests."));
}

static void dashboard() {
  Serial.println(F("PIR | RADAR | mic full dB | crow-band dB  ratio | BAT V  - any key to stop"));
  while (!keyPressed()) {
    MicFeatures f[2];
    bool ok = micReadBlock(f);
    const MicFeatures &m = f[micSlot()];
    static uint32_t last = 0;
    if (millis() - last >= 250) {
      last = millis();
      Serial.printf(" %d  |   %d   | %7.1f %s | %7.1f  %.2f | %.2f\n", digitalRead(PIN_PIR_OUT), digitalRead(PIN_RADAR_OUT),
                    m.rmsDbfs, ok && m.valid ? "   " : "BAD", m.bandDbfs, m.bandRatio, batteryVolts());
    }
  }
}

// Crow detector live: same code as the main firmware, prints every call it hears.
static void testCrow() {
  Serial.printf("Mic start-up: %s (slot %d)\n", micResume() ? "valid data" : "NO VALID DATA - check J1 wiring", micSlot());
  Serial.println(F("Crow detector live. Stay quiet 3 s (learning background), then play crow calls - any key to stop"));
  crowResumed();
  uint32_t t0 = millis(), lastLevel = 0, blocks = 0, bad = 0;
  while (!keyPressed()) {
    MicFeatures f[2];
    bool ok = micReadBlock(f);
    const MicFeatures &m = f[micSlot()];
    blocks++;
    if (!ok || !m.valid) bad++;
    if (millis() - t0 < 3000) { crowLearn(m); continue; }
    if (crowUpdate(m, millis()) == CrowResult::CONFIRMED) Serial.println(F("   >>> CROW CONFIRMED (main firmware would play now)"));
    if (millis() - lastLevel >= 1000) {
      lastLevel = millis();
      if (bad == blocks) Serial.printf("   mic: NO DATA in slot %d this second (check J1 wiring)\n", micSlot());
      else Serial.printf("   band %6.1f dB  background %6.1f  ratio %.2f  | bad blocks %u/%u\n", m.bandDbfs,
                         crowNoiseFloorDb(), m.bandRatio, bad, blocks);
      blocks = bad = 0;
    }
  }
}

void setup() {
  digitalWrite(PIN_RADAR_POWER, LOW);
  pinMode(PIN_RADAR_POWER, OUTPUT);
  pinMode(PIN_RADAR_OUT, INPUT);   // external R4 pull-down
  pinMode(PIN_PIR_OUT, INPUT);     // GPIO34: input-only, external R9 pull-down
  pinMode(PIN_BOOT_BTN, INPUT);    // external R6 pull-up
  Serial.begin(115200);
  delay(300);
  batteryBegin();
  bool drv = micBegin();
  Serial.printf("\nMic I2S init: %s, data %s\n", drv ? "OK" : "FAILED", drv && micResume() ? "valid" : "NOT valid");
  help();
}

void loop() {
  if (!Serial.available()) { delay(10); return; }
  char c = Serial.read();
  switch (c) {
    case 'b': testBattery(); break;
    case 'p':  // mic clocks stopped, like the main firmware while it sleeps waiting for the PIR
      micPause();
      Serial.println(F("Mic STOPPED during this test"));
      liveDigital("PIR", PIN_PIR_OUT);
      micResume();
      break;
    case 'P':
      Serial.println(F("Mic RUNNING during this test (compare with 'p')"));
      liveDigital("PIR", PIN_PIR_OUT);
      break;
    case 'r': if (!radarOn) { setRadar(true); Serial.println(F("Radar settling ~5 s...")); }
              liveDigital("RADAR", PIN_RADAR_OUT); break;
    case 'R': setRadar(!radarOn); break;
    case 'm': testMic(); break;
    case 'c': testCrow(); break;
    case 'd': testDf(); break;
    case 's': if (dfOk) df.stop(); Serial.println(F("DF stop")); break;
    case '+': volume = min(30, volume + 2); if (dfOk) df.volume(volume); Serial.printf("Volume %u\n", volume); break;
    case '-': volume = volume >= 2 ? volume - 2 : 0; if (dfOk) df.volume(volume); Serial.printf("Volume %u\n", volume); break;
    case 'k': liveDigital("BOOT(1=released)", PIN_BOOT_BTN); break;
    case 'a': if (!radarOn) setRadar(true); dashboard(); break;
    case 'h': help(); break;
    default: break;
  }
  if (c > ' ') Serial.println(F("\nReady (h = help)"));
}
