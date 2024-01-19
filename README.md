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


# Creating mapping
The setup relies a laptop running the python scripts sending commands to the api's on a micro on the same wifi network. In order to make the mapping, the camera needs to not move during the process and must be able to view the entire chain of LEDs. 
![image](https://github.com/Lazarus9000/led2dcalibration/assets/16942446/acdfa831-5200-4d75-b62f-58edecc71868)


My setup for calibration uses my canon camera connected to a laptop. Any integrated webcam or usb webcam will suffice, I just like to be able to have more control over focus and framing. Bear in mind that the point of view of the camera defines the location of the point of view for the mapped image.  
![20221222_222000](https://github.com/Lazarus9000/led2dcalibration/assets/16942446/820fbfaf-6ebd-4b11-bdb2-641eeb7db422)

Early video of proof of concept  
[![Proof of concept](http://img.youtube.com/vi/gUEcQgL-Y4M/0.jpg)](http://www.youtube.com/watch?v=gUEcQgL-Y4M)



# Setup for running 
I have a server running a container executing e.g. fireworks or snow script, sending the pixel values to an ESP32 which control the LEDs. 
I am considering making an implementation which runs on a raspi, directly connected to the LEDs, to avoid having to have a laptop/desktop/server running and support animated output.
