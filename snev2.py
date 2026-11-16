import time
import cv2
import numpy as np
import random
from wledMapper import Mapper, preview

#Snow like sne.py, but with more and smaller snowballs
#Add --preview to see the picture in a window

wled = Mapper("192.168.1.172", 600, "UDP", "calibration.txt")

#Change these to taste
numberOfSnowballs = 30
radius = 10          #sne.py uses 25
blur = 5             #sne.py uses 10, smaller balls need less blur to stay visible
size = 400           #the snow falls in a size x size picture that is mapped onto the LEDs
slowest = 0.2        #pixels a snowball falls per frame, sne.py uses 1 to 3
fastest = 0.7
#Color of the snow, each 0-255. Pure white is 255, 255, 255, the default is a bit warmer
red = 255
green = 180
blue = 150

class Snow:
    def __init__(self, var1, var2, var3):
        self.x = var1
        self.y = var2
        self.speed = var3

#Spread the snowballs over the picture and a bit above it, so they do not arrive in rows
snow_list = []
for i in range(numberOfSnowballs):
    snow_list.append(Snow(random.randint(0, size - 1), random.randint(-radius, size + radius), random.uniform(slowest, fastest)))

while True:

    image = np.zeros((size, size, 3), dtype='uint8')

    for snow in snow_list:
        snow.y = snow.y + snow.speed
        #When a snowball has left the bottom, start it again above the top at a new place
        if snow.y > size + 2 * radius:
            snow.y = -2 * radius
            snow.x = random.randint(0, size - 1)
            snow.speed = random.uniform(slowest, fastest)
        cv2.circle(image, (int(snow.x), int(snow.y)), radius, (blue, green, red), -1)   #OpenCV pictures are blue, green, red

    img2 = cv2.GaussianBlur(image, (0, 0), blur, cv2.BORDER_DEFAULT)
    preview("blur", img2)
    wled.image(img2, 100)
    time.sleep(0.0105)
