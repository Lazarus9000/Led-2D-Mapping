import time
import cv2
import numpy as np
from wledMapper import Mapper
import sys

#Call script e.g. "python flag.py spiral.png" to project image onto LEDS

imagepath = "dkdark.png"

#Read image path from args
if len(sys.argv) == 2:
    imagepath = sys.argv[1]

#Initiate wledMapper
wled = Mapper("192.168.1.172", 450, "UDP", "calibration.txt")

image = np.zeros((400, 400, 3), dtype='uint8')

#Load image
inputimg = cv2.imread(imagepath)
#Blur to avoid aliasing when projecting onto the lower resolution LEDs
img2 = cv2.GaussianBlur(inputimg,(0,0),10,cv2.BORDER_DEFAULT)

wled.image(img2,50)
