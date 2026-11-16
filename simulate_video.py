"""Render a fake recording of the calibration sequence, to try calibrate_video.py
and viewer.html without a LED chain or a camera.

    python simulate_video.py --leds 100 --out simulated.mp4
    python calibrate_video.py simulated.mp4 --leds 100 --step 0.3

The true LED positions are written next to the video (simulated_truth.txt) so the
result can be compared. A few LEDs are hidden and one has a reflection, like a
real setup, and the scene contains a lamp that is brighter than any LED.
"""
import argparse
import math
import os

import cv2
import numpy as np

from calibrate_sequence import build_timeline, timeline_duration


def led_positions(count, width, height):
    """A chain wound in a spiral, roughly like lights on a tree."""
    points = []
    for i in range(count):
        f = i / max(count - 1, 1)
        turns = 6
        radius = (0.08 + 0.34 * (1 - f)) * height
        angle = f * turns * 2 * math.pi
        x = width * 0.5 + radius * math.cos(angle) * 1.2
        y = height * (0.9 - 0.8 * f) + radius * 0.15 * math.sin(angle)
        points.append((x, y))
    return points


def main():
    parser = argparse.ArgumentParser(description="Render a simulated calibration recording.")
    parser.add_argument("--leds", type=int, default=100)
    parser.add_argument("--step", type=float, default=0.3)
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--out", default="simulated.mp4")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--clock-error", type=float, default=0.004,
                        help="how much faster the camera clock runs than the sequence (0.004 = 0.4%%)")
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    width, height = 1280, 720
    truth = led_positions(args.leds, width, height)
    hidden = set(int(i) for i in rng.choice(args.leds, size=max(1, args.leds // 20), replace=False))
    visible = [i for i in range(args.leds) if i not in hidden]
    reflecting = visible[len(visible) // 2]
    gain = rng.uniform(0.45, 1.0, size=args.leds)

    def blob(image, x, y, value, size):
        cv2.circle(image, (int(round(x * 8)), int(round(y * 8))), int(size * 8), float(value), -1,
                   cv2.LINE_AA, 3)

    scene = np.full((height, width), 12, np.float32)
    cv2.circle(scene, (150, 120), 40, 250.0, -1, cv2.LINE_AA)    # a lamp
    cv2.rectangle(scene, (900, 500), (1200, 700), 60.0, -1)      # a bright wall
    scene = cv2.GaussianBlur(scene, (0, 0), 6)

    everything = np.zeros((height, width), np.float32)
    for i in visible:
        blob(everything, truth[i][0], truth[i][1], 255 * gain[i], 4)
    everything = cv2.GaussianBlur(everything, (0, 0), 3)

    # Timeline as absolute times; the LEDs react a little late and unevenly (wifi)
    timeline = build_timeline(args.leds, args.step)
    edges = np.cumsum([0.0] + [d for d, _, _ in timeline])
    edges[1:-1] += rng.uniform(0.005, 0.035, size=len(edges) - 2)

    pre_roll = 1.7
    total = timeline_duration(timeline) + pre_roll + 2.3
    writer = cv2.VideoWriter(args.out, cv2.VideoWriter_fourcc(*"mp4v"), args.fps, (width, height))
    if not writer.isOpened():
        raise SystemExit("could not open %s for writing" % args.out)

    frames = int(total * args.fps)
    for n in range(frames):
        t = (n / args.fps) / (1 + args.clock_error) - pre_roll
        image = scene.copy()
        k = int(np.searchsorted(edges, t, side="right")) - 1
        if 0 <= k < len(timeline):
            _, kind, index = timeline[k]
            if kind == "all":
                image += everything
            elif kind == "led" and index not in hidden:
                led = np.zeros((height, width), np.float32)
                blob(led, truth[index][0], truth[index][1], 255 * gain[index], 4)
                if index == reflecting:
                    blob(led, truth[index][0] + 260, truth[index][1] + 40, 255 * gain[index] * 0.8, 4)
                image += cv2.GaussianBlur(led, (0, 0), 3)
        image += rng.normal(0, 2.5, size=image.shape).astype(np.float32)
        writer.write(cv2.cvtColor(np.clip(image, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR))
    writer.release()

    stem = os.path.splitext(args.out)[0]
    with open(stem + "_truth.txt", "w") as f:
        for x, y in truth:
            f.write("%.1f,%.1f\n" % (x, y))
    print("Wrote %s (%d frames, %.0f s) and %s_truth.txt" % (args.out, frames, total, stem))
    print("Hidden LEDs: %s" % sorted(hidden))
    print("LED with a reflection: %d" % reflecting)


if __name__ == "__main__":
    main()
