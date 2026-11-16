import time
import cv2
import numpy as np
from wledMapper import Mapper, preview, arguments
import sys

#Call script e.g. "python flag.py spiral.png" to project image onto LEDS

imagepath = "dkdark.png"

#Read image path from args
#(the --preview switch is handled by wledMapper and is not counted here)
args = arguments()
if len(args) == 1:
    imagepath = args[0]

#Initiate wledMapper
wled = Mapper("192.168.1.172", 600,"UDP", "calibration.txt")

image = np.zeros((400, 400, 3), dtype='uint8')

#Load image
inputimg = cv2.imread(imagepath)
#Blur to avoid aliasing when projecting onto the lower resolution LEDs
img2 = cv2.GaussianBlur(inputimg,(0,0),10,cv2.BORDER_DEFAULT)

preview("Background", img2)
wled.image(img2,25)
