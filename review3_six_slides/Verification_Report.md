# Review 3 deck verification

Verified against `Embedded_Review_3_Final.pdf` after exporting the rebuilt PowerPoint through Microsoft PowerPoint.

## File checks

- PowerPoint slides: **6**
- PDF pages: **6**
- Slides with embedded presenter notes: **6**
- Text shapes checked through PowerPoint: **121**
- Text overflow or clipping detected: **0**
- Objects outside the slide canvas: **0**
- HAL code or HAL API content: **none**

## Diagram checks

### Slide 2 — complete firmware flow

- Power-on, initialization, sensor warm-up and the recurring main checks are connected.
- Radar/PIR interrupts enter through the ISR notification path and do not directly trigger the speaker.
- Failed health checks lead to outputs OFF and fault recovery.
- Confirmed activity leads to the deterrent flow.
- Idle operation leads to the sleep flow only after the sleep decision.
- Every recovery, cooldown and wake path returns through connector **A** to the main checks.

### Slide 3 — detection and deterrence

- Confirmation requires **radar AND sound**; PIR is supporting evidence.
- A negative evidence check resets the consecutive-positive count.
- Fewer than three positives return to the next 100 ms check.
- Three positives start one burst with a maximum duration of 3 s.
- Health and events continue to be serviced during the burst.
- A detected fault turns the output off and transfers to Slide 6.
- Normal completion turns the output off, applies the 15 s cooldown, clears the count and returns to monitoring.

### Slide 4 — interrupt handling

- The ISR records the event source, notifies the main task and returns.
- Fresh sensor reads, detection decisions and playback control remain in the main task.
- The cross-lane arrow represents notification only.

### Slide 5 — power management

- Sleep requires healthy and idle operation, no pending work and a completed cooldown.
- Outputs are off and microphone acquisition is paused before sleep.
- A final event/input check can cancel sleep.
- Light sleep wakes from a motion GPIO level or RTC timer.
- Both wake and cancelled-sleep paths resume the microphone, read fresh sensors and return to connector A.

### Slide 6 — fault and watchdog handling

- Battery, sensor and audio faults converge on outputs OFF and inhibited actuation.
- Recovery remains inhibited until the relevant recovery condition is valid.
- The watchdog stall path is separate because a stalled task cannot run the software fault handler.
- A configured watchdog reset returns to the power-on path.

## Values still requiring hardware calibration

The supplied deck defines the 60 s warm-up, 50 ms audio block, 100 ms active check, three-positive confirmation, 3 s maximum burst, 15 s cooldown and 1 s awake health check as design targets. Battery thresholds, idle delay, RTC wake period, acoustic thresholds and stale-data limits remain configurable. The GPIO wake path assumes the chosen radar provides a suitable digital motion output.
