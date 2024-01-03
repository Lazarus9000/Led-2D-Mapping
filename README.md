# led2dcalibration
I wanted to be able to map images onto my LED chain which uses a ESP32 with WLED for control. After searching I couldn't find a solution, so I made an attempt myself.

Python library in wledMapper.py implements functions map colors of pixels on WLED chain to a picture.  
In order to achieve this calibration data must be obtained, which can be done with a camera and utilizing the library to turn on pixels one at a time and locate it using image processing, as implemented in calibrate.py. This outputs the calibration data into a file which can be reused - I've been able to reuse mine across an entire winter season.  
The library implements the JSON (https://kno.wled.ge/interfaces/json-api/) and UDP (https://kno.wled.ge/interfaces/udp-realtime/) interfaces on WLED controllers. May add more later, but currently the UDP interface sufficiently supports my needs. The JSON interface was limited in the amount of LEDS I could make it handle, and topped out at ~250 (likely 256, but I don't think I verified if it was that exact value).

Currently there are a few working examples  
Image.py - Takes a path to an image (jpg and png tested) as input and maps that onto LEDS  
sne.py - Generates images of snowballs falling down  
bangbangv3.py - Generates images of fireworks  


# My setup for calibration
Canon camera connected to laptop. Bear in mind that the point of view of the camera defines the location of the point of view for the mapped image.  


# Setup for running 
I have a server running a container executing e.g. fireworks or snow script, sending the pixel values to an ESP32 which control the LEDs. 
I am considering making an implementation which runs on a raspi, directly connected to the LEDs, to avoid having to have a laptop/desktop/server running and support animated output.