"""Play the calibration light sequence on the LED chain - no camera attached.

Record the chain with any camera (a phone on a tripod is fine) while this
script runs, then feed the video to calibrate_video.py.

The sequence is:
    start signal : every LED flashes 3 times
    pause        : everything off
    mapping      : LED 0, LED 1, ... each lit alone for --step seconds
    pause        : everything off
    end signal   : every LED flashes 2 times

Example:
    python calibrate_sequence.py --ip 192.168.1.172 --leds 600
"""
import argparse
import time

# Timing of the sequence. calibrate_video.py relies on these, so a video must be
# analysed with the same values it was recorded with.
LEAD_IN = 2.0        # seconds of darkness before the start signal
FLASH_ON = 0.5       # seconds every LED is lit during a flash
FLASH_OFF = 0.5      # seconds of darkness between flashes
START_FLASHES = 3
END_FLASHES = 2
GAP_STEPS = 4        # darkness between a signal and the mapping part, in LED steps


def build_timeline(num_leds, step):
    """Return the sequence as a list of (duration_in_seconds, kind, led_index).

    kind is "off" (all dark), "all" (all lit) or "led" (only led_index lit).
    """
    timeline = [(LEAD_IN, "off", None)]
    for i in range(START_FLASHES):
        timeline.append((FLASH_ON, "all", None))
        if i < START_FLASHES - 1:
            timeline.append((FLASH_OFF, "off", None))
    timeline.append((GAP_STEPS * step, "off", None))
    for i in range(num_leds):
        timeline.append((step, "led", i))
    timeline.append((GAP_STEPS * step, "off", None))
    for i in range(END_FLASHES):
        timeline.append((FLASH_ON, "all", None))
        timeline.append((FLASH_OFF, "off", None))
    return timeline


def timeline_duration(timeline):
    return sum(duration for duration, _, _ in timeline)


def main():
    parser = argparse.ArgumentParser(
        description="Play the calibration light sequence on a WLED chain while you record it on video.")
    parser.add_argument("--ip", required=True, help="IP address of the WLED controller")
    parser.add_argument("--leds", type=int, required=True, help="number of LEDs on the chain")
    parser.add_argument("--step", type=float, default=0.3,
                        help="seconds each LED stays lit (default 0.3). Use at least 4 video frames, "
                             "e.g. 0.15 or more for a 30 fps recording")
    parser.add_argument("--protocol", choices=["UDP", "JSON"], default="UDP")
    parser.add_argument("--brightness", type=int, default=255,
                        help="brightness 1-255 of the single mapping LED (default 255)")
    parser.add_argument("--flash-brightness", type=int, default=255,
                        help="brightness 1-255 of the all-LED start/end flashes (default 255). "
                             "Lower it if your power supply struggles with every LED on white")
    args = parser.parse_args()

    if args.leds < 1:
        parser.error("--leds must be at least 1")
    if args.step <= 0:
        parser.error("--step must be positive")
    for name in ("brightness", "flash_brightness"):
        if not 1 <= getattr(args, name) <= 255:
            parser.error("--%s must be between 1 and 255" % name.replace("_", "-"))
    from wledMapper import Mapper
    wled = Mapper(args.ip, args.leds, args.protocol, "")

    led_color = [args.brightness] * 3
    flash_color = [args.flash_brightness] * 3
    black = [0, 0, 0]

    def show(kind, index):
        if kind == "all":
            wled.allColor(flash_color, args.leds)
        elif kind == "led":
            colors = [black] * args.leds
            colors[index] = led_color
            wled.colors(colors)
        else:
            wled.allColor(black, args.leds)

    timeline = build_timeline(args.leds, args.step)
    total = timeline_duration(timeline)
    print("Sequence takes %.0f seconds for %d LEDs." % (total, args.leds))
    print("Camera tips: keep it perfectly still, lock exposure and focus, and make sure")
    print("the whole chain is in frame. Darker surroundings give cleaner results.")
    input("Start recording, then press Enter to start the sequence...")

    # Every state is scheduled against one clock, so delays do not add up over the run.
    start = time.perf_counter()
    deadline = start
    try:
        for duration, kind, index in timeline:
            deadline += duration
            if kind == "led" and index % 25 == 0:
                print("LED %d / %d" % (index, args.leds))
            show(kind, index)
            while True:
                remaining = deadline - time.perf_counter()
                if remaining <= 0:
                    break
                time.sleep(min(remaining, 0.05))
                # UDP packets can get lost, so repeat the current state while waiting
                if args.protocol == "UDP" and deadline - time.perf_counter() > 0.03:
                    show(kind, index)
    except KeyboardInterrupt:
        print("Interrupted - this recording can not be used.")
    finally:
        show("off", None)
        wled.release()

    print("Done. Stop the recording and run:")
    print("    python calibrate_video.py <your video> --leds %d --step %s" % (args.leds, args.step))


if __name__ == "__main__":
    main()
