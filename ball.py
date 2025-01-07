import time
import cv2
import numpy as np
import random
import colorsys
from wledMapper import Mapper


wled = Mapper("192.168.1.172", 450, "UDP", "calibration.txt")


class Ball:
    speed = 0.1
    x = 50
    y = 50
    xdir = 1
    ydir = 1
    scale = 10
    
    def __init__(self, speed, x, y, scale):
        self.speed = speed
        self.x = x
        self.y = y
        self.scale = scale
        
        
    
    def step(self, image):
        self.x = self.x+self.xdir*(self.speed*0.7)
        self.y = self.y+self.ydir*self.speed
        if (self.x + self.scale/2 > image.shape[0]) or (self.x - self.scale/2 < 0):
            self.xdir = self.xdir*-1
        
        if (self.y + self.scale/2 > image.shape[1]) or (self.y - self.scale/2 < 0):
            self.ydir = self.ydir*-1
        
        


rewind = 60
ball = Ball(0.6, 123, 50, 20)

while rewind > 0 :
    
    radius = 0
    
    
        
    image = np.zeros((400, 400, 3), dtype='uint8')
    #print(ball.x)
    #print(ball.y)
    cv2.circle(image, (int(ball.x), int(ball.y)), ball.scale, (255, 255, 255), -1)
    ball.step(image)    
    
    inputimg = image
    img2 = cv2.GaussianBlur(inputimg,(0,0),10,cv2.BORDER_DEFAULT)
    #cv2.imshow("blur", img2)
    #cv2.waitKey(1)
    wled.image(img2,100)

    
    time.sleep(0.0205)
    