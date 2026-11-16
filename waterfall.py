import time
import cv2
import numpy as np
from wledMapper import Mapper, preview, arguments
import sys

imagepath = "dkdark.png"

#Read image path from args
#(the --preview switch is handled by wledMapper and is not counted here)
args = arguments()
if len(args) == 1:
    imagepath = args[0]

#Initiate wledMapper
wled = Mapper("192.168.1.172", 600,"UDP", "calibration.txt")

#Load image
inputimg = cv2.imread(imagepath)
#Blur to avoid aliasing when projecting onto the lower resolution LEDs
#img2 = cv2.GaussianBlur(inputimg,(0,0),10,cv2.BORDER_DEFAULT)

animate = 0
img2 = cv2.imread(imagepath)
img3 = cv2.imread(imagepath)
img4 = cv2.flip(cv2.imread(imagepath), 0) 
(h, w) = img2.shape[:2]
while 1 > 0:
	#img3 = rotate(img2, angle, scale = 2)
	
	y_offset = int(animate*h)
	x_offset = 0
	x_end = x_offset + img3.shape[1]
	y_end = y_offset + img3.shape[0]
	
	y_offset2 = int(animate*h)
	
	img2[y_offset:y_end,x_offset:x_end] = img3[0:h-y_offset,0:w-x_offset]
	img2[0:y_offset2,x_offset:x_end] = img4[h-y_offset2:h,0:w-x_offset]
	#img4 = cv2.imread(imagepath)
	#img3 = fall(img2, img4, animate)
	animate = animate + 0.002
	if animate >= 1:
		animate = 0
		img3 = cv2.flip(img3,0)
		img4 = cv2.flip(img4,0)
    
	wled.image(img2,25)
	#print(animate)
	
	preview("Background", img2)
	time.sleep(0.05)
