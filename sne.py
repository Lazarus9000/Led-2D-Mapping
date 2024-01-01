import time
import cv2
import numpy as np
import random
import colorsys
from wledMapper import Mapper


wled = Mapper("192.168.1.172", 450, "UDP", "calibration.txt")

class Snow:
    def __init__(self, var1, var2, var3):
        self.x = var1
        self.y = var2
        self.speed = var3

snow_list = []
snow_list.append(Snow(50, -1, 5))
snow_list.append(Snow(150, -100, 5))
snow_list.append(Snow(250, 100, 5))
snow_list.append(Snow(350, 500, 5))
snow_list.append(Snow(100, 250, 5))
snow_list.append(Snow(300, -200, 5))

rewind = 60


while rewind > 0 :
    
    image = np.zeros((400, 400, 3), dtype='uint8')
    
    for snow in snow_list:
        snow.y = snow.y+snow.speed
        if snow.y > image.shape[1] + 100:
            snow.y = snow.y - image.shape[1] - 200
        cv2.circle(image, (snow.x,snow.y), 25, (255, 255, 255), -1)
    
    inputimg = image
    img2 = cv2.GaussianBlur(inputimg,(0,0),10,cv2.BORDER_DEFAULT)
    wled.image(img2,100)
    time.sleep(0.0105)
        
    #rewind -= 1