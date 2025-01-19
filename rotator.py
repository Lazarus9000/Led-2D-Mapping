import time
import cv2
import numpy as np
from wledMapper import Mapper
import sys

#https://stackoverflow.com/a/32929315
def rotate(image, angle, center = None, scale = 1.0):
    (h, w) = image.shape[:2]

    if center is None:
        center = (w / 2, h / 2)

    # Perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h))

    return rotated

imagepath = "dkdark.png"

#Read image path from args
if len(sys.argv) == 2:
    imagepath = sys.argv[1]

#Initiate wledMapper
wled = Mapper("192.168.1.172", 450, "UDP", "calibration.txt")

#Load image
inputimg = cv2.imread(imagepath)
#Blur to avoid aliasing when projecting onto the lower resolution LEDs
img2 = cv2.GaussianBlur(inputimg,(0,0),10,cv2.BORDER_DEFAULT)

angle = 0
img3 = img2
while 1 > 0:
	img3 = rotate(img2, angle, scale = 2)
	wled.image(img3,25)
	angle = angle + 0.1
	cv2.imshow("Background", img3)
	cv2.waitKey(1)
