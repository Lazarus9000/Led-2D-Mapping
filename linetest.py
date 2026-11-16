"""Test a calibration: sweep a line across the LEDs.

A horizontal line travels from top to bottom, then a vertical line travels from
left to right, and this repeats. With a good calibration both look like one
straight line moving across the chain. LEDs that light up away from the line are
mapped to the wrong place.

    python linetest.py --ip 192.168.1.172 --leds 600 --calibration calibration.txt

Stop with Ctrl+C.
"""
import argparse
import time

import cv2
import numpy as np

from wledMapper import Mapper, preview

SIZE = 400  # the line is drawn in a SIZE x SIZE picture that is mapped onto the LEDs


def main():
    parser = argparse.ArgumentParser(description="Sweep a line across the LEDs to check a calibration.")
    parser.add_argument("--ip", default="192.168.1.172", help="IP address of the WLED controller")
    parser.add_argument("--leds", type=int, default=600, help="number of LEDs on the chain")
    parser.add_argument("--calibration", default="calibration.txt", help="calibration file to test")
    parser.add_argument("--seconds", type=float, default=4.0, help="duration of one pass (default 4)")
    parser.add_argument("--width", type=float, default=6.0,
                        help="thickness of the line in percent of the picture (default 6)")
    parser.add_argument("--brightness", type=int, default=50, help="brightness in percent (default 50)")
    parser.add_argument("--preview", action="store_true",
                        help="show the picture that is sent to the LEDs in a window")
    parser.add_argument("--no-preview", action="store_true", help="no window (the default)")
    args = parser.parse_args()

    wled = Mapper(args.ip, args.leds, "UDP", args.calibration)
    if len(wled.normx) < args.leds:
        parser.error("%s has %d points, fewer than --leds %d"
                     % (args.calibration, len(wled.normx), args.leds))

    thickness = max(1, int(round(SIZE * args.width / 100)))
    # the line starts and ends just outside the picture, so it enters and leaves cleanly
    travel = SIZE + 2 * thickness
    frame_time = 1 / 30

    try:
        while True:
            for vertical_line in (False, True):
                start = time.perf_counter()
                while True:
                    progress = (time.perf_counter() - start) / args.seconds
                    if progress >= 1:
                        break
                    position = int(round(progress * travel)) - thickness
                    image = np.zeros((SIZE, SIZE, 3), dtype="uint8")
                    if vertical_line:
                        cv2.line(image, (position, 0), (position, SIZE - 1), (255, 255, 255), thickness)
                    else:
                        cv2.line(image, (0, position), (SIZE - 1, position), (255, 255, 255), thickness)
                    preview("Line test", image)
                    wled.image(image, args.brightness)
                    time.sleep(frame_time)
    except KeyboardInterrupt:
        pass
    finally:
        wled.allColor(wled.black, args.leds)
        wled.release()


if __name__ == "__main__":
    main()
