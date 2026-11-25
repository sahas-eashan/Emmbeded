#pragma once
// Pin map read from the routed PCB: PCB_Embedded_PCB_2026-11-25.pcbdoc
// (module pad -> net -> connector). ESP32-WROOM-32 pad numbers in brackets.
// See CONNECTIONS.md for the full connector-by-connector table.

// ---- Radar RCWL-0516 : connector U7 (1 = 5V_RADAR, 2 = GND, 3 = OUT) ----
constexpr int PIN_RADAR_OUT   = 21;  // [pad 33] via R5 series, R4 pull-down
constexpr int PIN_RADAR_POWER = 16;  // [pad 27] net RADAR_SWITCH -> Q3/Q2 high-side switch
                                     // HIGH = radar ON, LOW/floating = OFF (R16 pull-down)

// ---- PIR HC-SR501 : header U2 (1 = GND, 2 = OUT, 3 = 3V3) ----
constexpr int PIN_PIR_OUT     = 34;  // [pad 6] via R8 series, R9 pull-down (input-only pin)

// ---- Microphone INMP441 : connector J1 ----
// J1: 1 = GND, 2 = GND (use for L/R), 3 = GPIO33, 4 = GPIO25, 5 = GPIO26, 6 = 3V3
constexpr int PIN_MIC_SD      = 33;  // [pad 9]  J1-3 -> mic SD
constexpr int PIN_MIC_WS      = 25;  // [pad 10] J1-4 -> mic WS
constexpr int PIN_MIC_SCK     = 26;  // [pad 11] J1-5 -> mic SCK

// ---- DFPlayer Mini : connector P2 (1 = +5V, 2 = GND, 3 = DF RX, 4 = DF TX) ----
constexpr int PIN_DF_TX       = 17;  // [pad 28] ESP TX -> R17 1k -> P2-3 -> DFPlayer RX
constexpr int PIN_DF_RX       = 18;  // [pad 30] ESP RX <- P2-4 <- DFPlayer TX

// ---- Battery sense : BAT_P -> R10 -> GPIO35 -> R11 -> GND, C8 filter ----
constexpr int PIN_BATT_SENSE  = 35;  // [pad 7] ADC1_CH7, input-only

// ---- Buttons ----
constexpr int PIN_BOOT_BTN    = 0;   // [pad 25] SW2 via R7, R6 pull-up (pressed = LOW)
// SW1 = reset (EN). The power LED is hard-wired to +5V, not a GPIO.
// The PAM8403 amplifier is powered from P1 (+5V, GND) and is always on.
