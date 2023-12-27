import time
import cv2
import numpy as np
import wledAPI
import sys

#Call e.g. python flag.py spiral.png to project image onto LEDS

imagepath = "dkdark.png"
if len(sys.argv) == 2:
    imagepath = sys.argv[1]

wledAPI.wled("192.168.1.172", 450, "UDP", "calibration.txt")

image = np.zeros((400, 400, 3), dtype='uint8')

inputimg = cv2.imread(imagepath)
img2 = cv2.GaussianBlur(inputimg,(0,0),10,cv2.BORDER_DEFAULT)

wledAPI.image(img2,50)
