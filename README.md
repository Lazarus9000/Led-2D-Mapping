# 2D Led Mapping
I wanted to be able to map images onto my LED chain, which uses a ESP32 with WLED for control. After searching I couldn't find a solution, so I made one myself.

Python library in wledMapper.py implements functions map colors of pixels on WLED chain to a picture.  
In order to achieve this calibration data must be obtained, which can be done with a camera and utilizing the library to turn on pixels one at a time and locate it using image processing, as implemented in calibrate.py. This outputs the calibration data into a file which can be reused - I've been able to reuse mine across an entire winter season.  
The library implements the JSON (https://kno.wled.ge/interfaces/json-api/) and UDP (https://kno.wled.ge/interfaces/udp-realtime/) interfaces on WLED controllers. May add more later, but currently the UDP interface sufficiently supports my needs. The JSON interface was limited in the amount of LEDS I could make it handle, and topped out at ~250 (likely 256, but I don't think I verified if it was that exact value).

I've written a few examples utilizing the library  
Image.py - Takes a path to an image (jpg and png tested) as input and maps that onto LEDS  

sne.py - Generates images of snowballs falling down https://youtu.be/DdPqfmr4xdM  
![Snow_LED_chain](https://github.com/Lazarus9000/Led-2D-Mapping/assets/16942446/627a164d-1817-4835-ab53-a078ad05d186)


bangbangv3.py - Generates images of fireworks https://youtu.be/MvkPpxqalhs 
![Fireworks_mapped_to_LEDs](https://github.com/Lazarus9000/Led-2D-Mapping/assets/16942446/4b5517f0-5524-4572-997a-08111de4ed59)

[But can it run doom?](https://youtu.be/DqW8ubmIXaI)\
Yeah, but as expected the resolution and space between the LEDs make it a pretty bad display for it :) You can try for yourself using the doom.py, but you need to provide your own WAD

Wrote two scripts specifically for gradient colors moving slowly.\ 
Waterfall.py will continuously have an image falling, followed by a version of it which has been vertically flipped to provide a continuous gradient moving over the chain\
Rotator.py will scale an image and continuously rotate it

All scripts run without opening a window, so they also work on a server without a screen. Add `--preview` to see the picture that is sent to the LEDs in a window on the computer, e.g. `python rotator.py image2.jpg --preview`.

# Creating mapping
The setup relies a laptop running the python scripts sending commands to the api's on a micro on the same wifi network. In order to make the mapping, the camera needs to not move during the process and must be able to view the entire chain of LEDs. 
![image](https://github.com/Lazarus9000/led2dcalibration/assets/16942446/acdfa831-5200-4d75-b62f-58edecc71868)


My setup for calibration uses my canon camera connected to a laptop. Any integrated webcam or usb webcam will suffice, I just like to be able to have more control over focus and framing. Bear in mind that the point of view of the camera defines the location of the point of view for the mapped image.  
![20221222_222000](https://github.com/Lazarus9000/led2dcalibration/assets/16942446/820fbfaf-6ebd-4b11-bdb2-641eeb7db422)

Early video of proof of concept  
[![Proof of concept](http://img.youtube.com/vi/gUEcQgL-Y4M/0.jpg)](http://www.youtube.com/watch?v=gUEcQgL-Y4M)



# Creating mapping from a recorded video
The mapping can also be made without a camera connected to the computer. The LEDs play a light sequence, you record it with any camera (a phone works well, no app needed), and the video is analysed afterwards.

1. Put the camera on a tripod or lean it against something so it can not move, with the whole chain in view. Lock exposure and focus if the camera allows it (on most phones: press and hold on the picture). Darker surroundings give cleaner results.
2. Start recording, then play the sequence:
   ```
   python calibrate_sequence.py --ip 192.168.1.172 --leds 600
   ```
   All LEDs flash three times (start signal), then each LED lights up alone for 0.3 seconds, then all LEDs flash twice (end signal). 600 LEDs take a little over three minutes. `--step` changes the time per LED; keep it at 4 video frames or more.
3. Stop recording, copy the video to the computer and analyse it:
   ```
   python calibrate_video.py recording.mp4 --leds 600 --step 0.3
   ```

The start and end signals are found automatically, so it does not matter how much extra video there is before and after, and the time per LED is measured from the video itself. The result is

- `calibration.txt` - the same format as the live calibration, ready for wledMapper
- `calibration.json` - the same points plus how well each LED was detected, for the viewer below
- `calibration_reference.jpg` - a frame with all LEDs lit, used as backdrop in the viewer

Several recordings of the sequence from the same camera position can be given at once (`python calibrate_video.py take1.mp4 take2.mp4 --leds 600`). For every LED the recording that saw it best is used.

If the flashes are not recognised, `--start-time` and `--end-time` set the moment the last start flash ends and the first end flash begins by hand (seconds into the video).

To try it without LEDs or camera, `python simulate_video.py --leds 100` renders a fake recording.

# Reviewing and correcting the mapping
Open `viewer.html` in a browser (double-click it, nothing to install) and drop a `calibration.json` or `calibration.txt` on the page. Dropping the `_reference.jpg` as well shows the points on top of the camera picture.

Every LED gets a confidence between 0 and 1, which is the product of

- how well it was detected in the video: bright enough, the only bright spot, and in the same place in every frame (only available in `calibration.json`)
- how well it fits the LEDs next to it on the chain: a point far away from all its neighbours is probably a wrong detection
- whether it shares its spot with several other LEDs: failed detections tend to all land on the same lamp or reflection

The slider sets the lowest confidence that is accepted. LEDs below it get a calculated position instead: by default evenly spaced between the nearest accepted LEDs before and after it, or alternatively the average of the last two accepted LEDs before it.

Points can be dragged to correct them by hand, and a point that is moved by hand is always accepted. Double-click a point to undo its correction. Undo/redo, zooming, panning and nudging with the arrow keys work as expected, and hovering or clicking a point shows its details.

`Export calibration.txt` saves the corrected mapping for wledMapper. `Save session` keeps the original detections together with the corrections and the threshold, so the work can be continued later.

To check a mapping on the LEDs, `python linetest.py --ip 192.168.1.172 --leds 600 --calibration calibration.txt` sweeps a horizontal line from top to bottom and then a vertical line from left to right, in a loop. LEDs that light up away from the line are mapped to the wrong place.

# Setup for running 
I have a server running a container executing e.g. fireworks or snow script, sending the pixel values to an ESP32 which control the LEDs. 
I am considering making an implementation which runs on a raspi, directly connected to the LEDs, to avoid having to have a laptop/desktop/server running and support animated output.
