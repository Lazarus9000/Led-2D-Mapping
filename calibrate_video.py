"""Create calibration data from a recorded video instead of a live camera.

Record the chain while calibrate_sequence.py plays its light sequence, then run:

    python calibrate_video.py recording.mp4 --leds 600 --step 0.3

Several recordings of the same sequence, taken from the same camera position,
can be given at once. For every LED the recording with the best detection wins.

Output (names follow --out, default calibration.txt):
    calibration.txt            x,y per LED - the format wledMapper reads
    calibration.json           the same points plus detection quality per LED,
                               open it in viewer.html to review and correct
    calibration_reference.jpg  frame with every LED lit, a backdrop for the viewer
"""
import argparse
import json
import math
import os
import sys

import cv2
import numpy as np

from calibrate_sequence import GAP_STEPS, START_FLASHES, END_FLASHES

PROCESS_SIZE = 960      # frames are scaled down to this (longest side) for analysis
WINDOW = (0.2, 0.8)     # part of each LED's time slot that is used, avoids the transitions
MAX_SLOT_FRAMES = 12    # more frames than this per LED do not improve the result
MAX_GAP_FRAMES = 15


class CalibrationError(Exception):
    pass


def warn(message):
    print("WARNING: " + message)


# --------------------------------------------------------------------------
# Pass 1: brightness of every frame, used to find the start and end signals
# --------------------------------------------------------------------------

def read_brightness(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise CalibrationError("could not open video: %s" % path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    stamps = []
    thumbnails = []
    size = None
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        stamps.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
        if size is None:
            size = (frame.shape[1], frame.shape[0])
        small = cv2.resize(frame, (128, 72), interpolation=cv2.INTER_AREA)
        thumbnails.append(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY))
    cap.release()
    if len(thumbnails) < 10:
        raise CalibrationError("video has too few readable frames: %s" % path)

    # Brightness = light added on top of the usual scene. For most of the video a
    # single LED is lit, so the per-pixel median over time is the scene without LEDs.
    # Measuring only what is added keeps the flashes visible even when the LEDs
    # cover a small part of a bright picture.
    sample = np.round(np.linspace(0, len(thumbnails) - 1, min(len(thumbnails), 200))).astype(int)
    scene = np.median(np.stack([thumbnails[i] for i in sample]), axis=0).astype(np.float32)
    brightness = [float(np.clip(t.astype(np.float32) - scene, 0, None).mean()) for t in thumbnails]

    # Prefer the real timestamps (phones record with a variable frame rate) and
    # fall back to frame number / fps when the container does not provide them.
    times = np.array(stamps)
    usable = np.all(np.isfinite(times)) and np.all(np.diff(times) > 0)
    if not usable:
        if not fps or fps <= 0 or not math.isfinite(fps):
            raise CalibrationError("video has neither usable timestamps nor a frame rate: %s" % path)
        times = np.arange(len(brightness)) / fps
    return times, np.array(brightness), size


def find_pulses(times, brightness):
    """Return [(rise_time, fall_time), ...] for every all-LED flash in the video."""
    padded = np.concatenate(([brightness[0]], brightness, [brightness[-1]]))
    smooth = np.median(np.stack([padded[:-2], padded[1:-1], padded[2:]]), axis=0)
    low = float(np.median(smooth))
    high = float(smooth.max())
    noise = 1.4826 * float(np.median(np.abs(smooth - low)))
    if high - low < max(0.02, 8 * noise):
        raise CalibrationError(
            "could not see the start/end flashes: the overall brightness of the video hardly changes. "
            "Check that the whole sequence was recorded, or give --start-time and --end-time.")
    above = smooth > low + 0.4 * (high - low)

    pulses = []
    i = 0
    n = len(above)
    while i < n:
        if not above[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and above[j + 1]:
            j += 1
        rise = times[i] if i == 0 else (times[i - 1] + times[i]) / 2
        fall = times[j] if j == n - 1 else (times[j] + times[j + 1]) / 2
        pulses.append((float(rise), float(fall)))
        i = j + 1
    return pulses


def find_mapping_interval(times, brightness):
    """Return (end of the start signal, start of the end signal) in seconds."""
    pulses = find_pulses(times, brightness)
    print("  flashes found at: " + ", ".join("%.2f-%.2fs" % p for p in pulses))
    if len(pulses) < 2:
        raise CalibrationError(
            "found %d flash(es), need the start signal and the end signal. Was the recording "
            "stopped too early? You can also give --start-time and --end-time." % len(pulses))
    # The mapping part is by far the longest stretch between two flashes.
    gaps = [pulses[k + 1][0] - pulses[k][1] for k in range(len(pulses) - 1)]
    k = int(np.argmax(gaps))
    if k + 1 != START_FLASHES or len(pulses) - k - 1 != END_FLASHES:
        warn("expected %d start and %d end flashes but found %d and %d. Continuing with the "
             "longest dark stretch between flashes as the mapping part - check the result."
             % (START_FLASHES, END_FLASHES, k + 1, len(pulses) - k - 1))
    return pulses[k][1], pulses[k + 1][0]


# --------------------------------------------------------------------------
# Pass 2: locate each LED
# --------------------------------------------------------------------------

def frames_between(times, start, end, limit):
    idx = np.nonzero((times >= start) & (times <= end))[0]
    if len(idx) > limit:
        idx = idx[np.round(np.linspace(0, len(idx) - 1, limit)).astype(int)]
    return [int(i) for i in idx]


def locate(frames, background, sigma, radius):
    """Find the lit LED in the frames of one time slot.

    Returns x, y (sub-pixel, in the scaled-down frame), the peak brightness above
    the background, the strongest other bright spot, and the share of frames that
    individually agree with the position.
    """
    mean = np.mean(frames, axis=0)
    blur = cv2.GaussianBlur(np.clip(mean - background, 0, None), (0, 0), sigma)
    _, peak, _, loc = cv2.minMaxLoc(blur)
    if peak <= 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    px, py = loc

    agree = 0
    for frame in frames:
        single = cv2.GaussianBlur(np.clip(frame - background, 0, None), (0, 0), sigma)
        _, _, _, (fx, fy) = cv2.minMaxLoc(single)
        if math.hypot(fx - px, fy - py) <= radius:
            agree += 1
    stability = agree / len(frames)

    # Refine to the centre of the bright blob rather than its single brightest pixel
    r = int(math.ceil(2 * sigma))
    x0, x1 = max(px - r, 0), min(px + r + 1, blur.shape[1])
    y0, y1 = max(py - r, 0), min(py + r + 1, blur.shape[0])
    weights = np.clip(blur[y0:y1, x0:x1] - 0.5 * peak, 0, None)
    total = float(weights.sum())
    ys, xs = np.mgrid[y0:y1, x0:x1]
    cx = float((weights * xs).sum() / total)
    cy = float((weights * ys).sum() / total)

    masked = blur.copy()
    cv2.circle(masked, (px, py), int(radius), 0, -1)
    second = float(masked.max())
    return cx, cy, float(peak), second, stability


def analyse_video(path, num_leds, step, start_time, end_time):
    print("Analysing %s" % path)
    times, brightness, (width, height) = read_brightness(path)
    duration = times[-1] - times[0]
    print("  %d frames, %dx%d, %.1f s" % (len(times), width, height, duration))

    if start_time is not None:
        t_start, t_end = start_time, end_time
    else:
        t_start, t_end = find_mapping_interval(times, brightness)
    span = t_end - t_start
    if span <= 0:
        raise CalibrationError("the end signal must come after the start signal")

    if num_leds is None:
        num_leds = int(round(span / step)) - 2 * GAP_STEPS
        if num_leds < 1:
            raise CalibrationError("the mapping part of the video is too short for --step %s" % step)
        print("  number of LEDs derived from --step: %d" % num_leds)
    measured = span / (num_leds + 2 * GAP_STEPS)
    print("  measured time per LED: %.4f s" % measured)
    if step is not None and abs(measured - step) > 0.05 * step:
        raise CalibrationError(
            "the video shows %.4f s per LED for %d LEDs, but --step says %s. The LED count or "
            "step does not match the recording, or the start/end signal was misread."
            % (measured, num_leds, step))

    # Which frames belong to which LED
    first = t_start + GAP_STEPS * measured
    slot_frames = []
    for i in range(num_leds):
        slot = first + i * measured
        idx = frames_between(times, slot + WINDOW[0] * measured, slot + WINDOW[1] * measured,
                             MAX_SLOT_FRAMES)
        if not idx:
            # no frame in the safe window: accept the frame closest to the middle of the slot
            near = int(np.argmin(np.abs(times - (slot + 0.5 * measured))))
            if slot + 0.1 * measured <= times[near] <= slot + 0.9 * measured:
                idx = [near]
        slot_frames.append(idx)
    counts = [len(idx) for idx in slot_frames]
    if np.median(counts) < 2:
        raise CalibrationError(
            "fewer than 2 usable video frames per LED (%.3f s per LED). Either the start/end "
            "signal was misread - compare the flashes listed above with the video - or the "
            "sequence is too fast for this frame rate: record with a higher frame rate or play "
            "the sequence with a longer --step." % measured)

    gap = GAP_STEPS * measured
    dark_start = frames_between(times, t_start + 0.35 * gap, t_start + 0.9 * gap, MAX_GAP_FRAMES)
    dark_end = frames_between(times, t_end - 0.9 * gap, t_end - 0.35 * gap, MAX_GAP_FRAMES)
    if not dark_start:
        raise CalibrationError("no video frames in the dark pause after the start signal")
    reference_index = int(np.argmax(brightness))

    role = {}  # frame index -> list of (kind, slot)
    for i in dark_start:
        role.setdefault(i, []).append(("dark_start", None))
    for i in dark_end:
        role.setdefault(i, []).append(("dark_end", None))
    for slot, idx in enumerate(slot_frames):
        for i in idx:
            role.setdefault(i, []).append(("led", slot))
    last_needed = max(max(role), reference_index)

    scale = min(1.0, PROCESS_SIZE / max(width, height))
    proc_w = max(1, int(round(width * scale)))
    proc_h = max(1, int(round(height * scale)))
    sigma = max(1.5, 4.0 * max(proc_w, proc_h) / PROCESS_SIZE)
    radius = max(6 * sigma, 0.03 * max(proc_w, proc_h))

    cap = cv2.VideoCapture(path)
    dark_frames = {"dark_start": [], "dark_end": []}
    background = None
    pending = {}
    results = [None] * num_leds
    reference = None
    for index in range(last_needed + 1):
        ok, frame = cap.read()
        if not ok:
            break
        if index == reference_index:
            reference = frame.copy()
        if index not in role:
            continue
        if scale < 1.0:
            frame = cv2.resize(frame, (proc_w, proc_h), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
        for kind, slot in role[index]:
            if kind != "led":
                dark_frames[kind].append(gray)
                if kind == "dark_start" and len(dark_frames[kind]) == len(dark_start):
                    background = np.median(dark_frames[kind], axis=0).astype(np.float32)
                continue
            pending.setdefault(slot, []).append(gray)
            if len(pending[slot]) == len(slot_frames[slot]):
                results[slot] = locate(pending.pop(slot), background, sigma, radius)
        if (index + 1) % 500 == 0:
            print("  frame %d / %d" % (index + 1, last_needed + 1))
    cap.release()
    if background is None:
        raise CalibrationError("could not read the dark frames after the start signal")

    if dark_frames["dark_end"]:
        drift = float(np.mean(np.abs(np.median(dark_frames["dark_end"], axis=0) - background)))
        if drift > 3.0:
            warn("the scene before the end signal looks different from the scene after the start "
                 "signal (%.1f grey levels on average). The camera may have moved or its exposure "
                 "or the room lighting changed during the recording." % drift)

    peaks = np.array([r[2] if r else 0.0 for r in results])
    typical = float(np.percentile(peaks, 75))
    if typical < 3.0:
        warn("the LEDs are barely brighter than the background. Expect poor results.")

    points = []
    for i, r in enumerate(results):
        if r is None or r[2] <= 0 or typical <= 0:
            points.append({"x": None, "y": None, "detection": 0.0, "strength": 0.0,
                           "uniqueness": 0.0, "stability": 0.0, "frames": counts[i]})
            continue
        cx, cy, peak, second, stability = r
        # strength: brightness compared to a typical LED in this video
        strength = float(np.clip((peak / typical - 0.08) / (0.35 - 0.08), 0, 1))
        # uniqueness: 1 when no other spot is more than half as bright
        uniqueness = float(np.clip((1 - second / peak) / 0.5, 0, 1))
        points.append({
            "x": round((cx + 0.5) / scale - 0.5, 1),
            "y": round((cy + 0.5) / scale - 0.5, 1),
            "detection": round(strength * uniqueness * stability, 3),
            "strength": round(strength, 3),
            "uniqueness": round(uniqueness, 3),
            "stability": round(stability, 3),
            "frames": counts[i],
        })

    clear = [p["stability"] for p in points if p["strength"] >= 1.0]
    if clear and float(np.mean(clear)) < 0.8:
        warn("the lit LED often jumps within a single time slot, which means the timing is off. "
             "Check --leds / --step, and that the flashes were found correctly.")
    missing = [i for i, c in enumerate(counts) if c == 0]
    if missing:
        warn("no video frame for LED(s) %s (dropped frames?)" % ", ".join(map(str, missing)))

    return {"points": points, "width": width, "height": height, "reference": reference}


# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Create LED calibration data from video(s) of the calibrate_sequence.py light sequence.")
    parser.add_argument("videos", nargs="+", help="one or more recordings of the sequence")
    parser.add_argument("--leds", type=int, help="number of LEDs the sequence was played with")
    parser.add_argument("--step", type=float,
                        help="the --step the sequence was played with (0.3 unless you changed it). "
                             "Used to verify the timing, or to derive --leds when that is not given")
    parser.add_argument("--out", default="calibration.txt", help="output file (default calibration.txt)")
    parser.add_argument("--start-time", type=float,
                        help="manual override: second in the video where the last start flash ends")
    parser.add_argument("--end-time", type=float,
                        help="manual override: second in the video where the first end flash begins")
    args = parser.parse_args()

    if args.leds is None and args.step is None:
        parser.error("give --leds (and preferably --step as well)")
    if args.leds is not None and args.leds < 1:
        parser.error("--leds must be at least 1")
    if args.step is not None and args.step <= 0:
        parser.error("--step must be positive")
    if (args.start_time is None) != (args.end_time is None):
        parser.error("--start-time and --end-time must be given together")
    if args.start_time is not None and len(args.videos) > 1:
        parser.error("--start-time/--end-time can only be used with a single video")

    try:
        runs = [analyse_video(v, args.leds, args.step, args.start_time, args.end_time)
                for v in args.videos]
        num_leds = len(runs[0]["points"])
        for video, run in zip(args.videos, runs):
            if len(run["points"]) != num_leds:
                raise CalibrationError("the videos do not contain the same number of LEDs; give --leds")
            if (run["width"], run["height"]) != (runs[0]["width"], runs[0]["height"]):
                raise CalibrationError(
                    "%s has a different resolution than %s. Videos can only be combined when they "
                    "are taken from the same camera position with the same settings."
                    % (video, args.videos[0]))
    except CalibrationError as error:
        sys.exit("ERROR: %s" % error)

    # For every LED keep the recording that saw it best
    points = []
    for i in range(num_leds):
        best = max(range(len(runs)), key=lambda r: runs[r]["points"][i]["detection"])
        point = dict(runs[best]["points"][i])
        point["video"] = best
        points.append(point)

    # An LED without any position gets the position of the nearest located LED on the
    # chain, so the files stay complete. Its detection of 0 flags it for the viewer.
    located = [i for i, p in enumerate(points) if p["x"] is not None]
    if not located:
        sys.exit("ERROR: no LED could be located in the video(s)")
    for i, p in enumerate(points):
        if p["x"] is None:
            nearest = min(located, key=lambda j: abs(j - i))
            p["x"], p["y"] = points[nearest]["x"], points[nearest]["y"]

    stem = os.path.splitext(args.out)[0]
    with open(args.out, "w") as f:
        for p in points:
            f.write("%d,%d\n" % (int(round(p["x"])), int(round(p["y"]))))
    with open(stem + ".json", "w") as f:
        json.dump({
            "format": "led-2d-mapping-calibration",
            "version": 1,
            "width": runs[0]["width"],
            "height": runs[0]["height"],
            "videos": [os.path.basename(v) for v in args.videos],
            "points": points,
        }, f, indent=1)
    written = [args.out, stem + ".json"]
    if runs[0]["reference"] is not None:
        cv2.imwrite(stem + "_reference.jpg", runs[0]["reference"])
        written.append(stem + "_reference.jpg")

    weak = [i for i, p in enumerate(points) if p["detection"] < 0.5]
    print("Located %d LEDs, %d of them with a weak detection (below 0.5)%s"
          % (num_leds, len(weak), ": " + ", ".join(map(str, weak)) if weak else ""))
    print("Wrote " + ", ".join(written))
    print("Open viewer.html in a browser and load %s to review and correct the mapping." % (stem + ".json"))


if __name__ == "__main__":
    main()
