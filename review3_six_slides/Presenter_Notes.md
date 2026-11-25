# Bird Repellent System — Review 3 presenter notes

Six slides; aim for about 4–5 minutes in total. Spend roughly 40–50 seconds on each slide, pointing to the relevant arrows instead of reading every box. These notes describe the proposed firmware design, not measured hardware performance.

## Slide 1 — System overview

Our project is a bird repellent system for indoor and swimming pool areas. This review explains the firmware flow, including interrupt handling and power management. The ESP32 receives motion information from the radar and PIR sensors and acoustic evidence from the microphone. When the confirmation rule is satisfied, it commands the DFPlayer and amplifier to play a short deterrent sound through the speaker. The main operating states are monitoring, deterrence, cooldown, idle sleep, and fault recovery. The next slides show how the firmware moves between these states.

## Slide 2 — Complete firmware flowchart

At power-on, the firmware first keeps the audio output off. It initializes the required interfaces, events, and timers, then allows about sixty seconds for sensor warm-up. Once ready, the main task checks system health and pending events. A healthy system evaluates fresh sensor evidence. A confirmed event starts a short burst, followed by a cooldown, and then returns to monitoring. When there is no work and the sleep conditions are satisfied, it enters light sleep. Any detected fault redirects the flow to recovery with the output off. Both wake-up and recovery return through the main checks.

## Slide 3 — Detection and deterrence

Detection uses fresh radar and microphone evidence together; the PIR reading provides additional support. We require three consecutive positive checks, scheduled every one hundred milliseconds while active. If a check is negative, the confirmation count resets. After confirmation, the firmware starts the deterrent sound and limits it to three seconds. It continues checking events and health during playback, so a detected fault can stop the output early. A normal burst ends with the output off and a fifteen-second cooldown. Events during cooldown do not start another burst. The system then clears the confirmation state and re-arms.

## Slide 4 — Interrupt handling and timing

The interrupt service routine has a small job. When a radar or PIR GPIO event occurs, it records the event source, notifies the main task, and returns. The main task reads fresh values and makes the detection decision. This keeps sensor processing and playback control out of the interrupt handler. Our proposed schedule uses fifty-millisecond audio blocks, one-hundred-millisecond active detection checks, and battery and health checks every second while awake. Burst and cooldown deadlines use elapsed time, so the firmware can keep servicing events while it waits. An interrupt is an event notification, not automatic permission to activate the sound.

## Slide 5 — Power management and wake-up

Before sleeping, the firmware confirms that the burst and cooldown have finished, no work is pending, and the motion inputs are quiet for the configured idle interval. It turns outputs off, finishes pending audio commands, pauses microphone acquisition, and arms GPIO and timer wake-up. It checks the inputs and pending events again before entering light sleep. Radar and PIR remain powered. A configured motion level or timer wakes the ESP32. The firmware resumes the microphone and obtains fresh data before returning to the main checks. Sound alone does not wake this design because microphone capture is paused during sleep.

## Slide 6 — Fault protection and recovery

Fault handling gives priority to keeping the audio output off. Low or invalid battery readings inhibit actuation. Battery recovery uses a higher threshold than the low-battery limit to prevent rapid switching between states. Missing or stale sensor data requires a successful fresh-data check before recovery. An audio output fault stays inhibited until restart and a successful self-check. The recovery path includes cooldown before re-arming. A configured watchdog monitors task progress and resets the controller if progress stops; it is fed only when useful work is progressing. These are proposed safeguards that still need verification with the actual hardware.

## Preparation notes — not additional slides

- **Detection-rule correction:** Source slide 5 says “Radar or sound?” but its note and later examples require radar **and** sound. The condensed presentation follows the AND rule; sound alone does not trigger deterrence. PIR is supporting evidence.
- **Design targets:** About 60 s warm-up, 50 ms audio blocks, 100 ms active detection checks, three consecutive positives, a maximum 3 s burst, a 15 s cooldown, and 1 s awake health checks come from the supplied presentation. Present these as proposed timings, not measurements or proven performance. Do not claim an exact confirmation latency from the three-check rule alone.
- **Configurable values:** The source does not specify battery voltage limits, the idle delay, timer wake period, acoustic thresholds, or sensor-staleness limits. Select these for the actual hardware and calibration results. Battery recovery must be above the low threshold.
- **Radar wake assumption:** The GPIO wake path assumes the selected radar provides a suitable digital motion output. Verify the actual sensor interface, signal levels, and pin arrangement. A UART-only radar would require a different wake arrangement.
- **Sleep behavior:** Radar and PIR stay powered; microphone acquisition pauses. Sound alone cannot wake this proposed design. Detection after wake must use newly acquired evidence.
- **Do not overclaim:** These charts define intended firmware behavior. They do not demonstrate measured battery life, reliable bird classification, deterrence effectiveness, or tested fault-stop latency.
- **Watchdog wording:** Say “configured watchdog reset”; reset behavior and timeout require deliberate configuration. The design must accommodate intended sleep and waiting periods.

## Supporting references

Project behavior and timing targets are condensed from `Embedded_Review_3_Final.pdf`. The following official documentation supports implementation planning; it does not validate this project's performance:

- [Espressif: ESP32 sleep modes](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/sleep_modes.html) — light-sleep behavior and GPIO/timer wake sources.
- [Espressif: ESP32 watchdogs](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/wdts.html) — task-progress monitoring and configurable watchdog behavior.
- [Espressif: ESP32 I2S](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/i2s.html) — microphone data acquisition if the selected microphone uses I2S.
