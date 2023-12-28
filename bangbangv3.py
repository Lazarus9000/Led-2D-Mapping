import time
import cv2
import numpy as np
import random
import colorsys
from wledMapper import Mapper


wled = Mapper("192.168.1.172", 450, "UDP", "calibration.txt")


class Rocket:
    speed = 0
    x = 0
    y = 0
    scale = 0
    delay = random.randrange(5,20)
    
    def __init__(self, var1, var2):
        self.xlimit = var1
        self.ylimit = var2
        self.reset()
        
    
    def reset(self):
        self.x = random.randrange(self.xlimit*0.25, self.xlimit-self.xlimit*0.25)
        self.y = random.randrange(self.ylimit*0.25, self.xlimit-self.ylimit*0.25)
        self.scale = random.randrange(10,100)
        self.speed = random.randrange(10,100)
        self.life = 100
        self.delay = random.randrange(5,80)
        #Set new color
        self.hue = random.randint(0, 180)
        #color = cv2.cvtColor(np.uint8([hue, 255, 255]), cv2.COLOR_HSV2BGR_FULL)
        (self.h, self.s, self.v) = (self.hue / 255, 1, 1)
        #convert to RGB
        (self.r, self.g, self.b) = colorsys.hsv_to_rgb(self.h, self.s, self.v)
        #expand RGB range
        (self.r, self.g, self.b) = (int(self.r * 100), int(self.g * 100), int(self.b * 100))
        #bangcolor = (r, g, b)
    
    def step(self):
        if self.life < 0:
            self.x = -500
            self.delay -= 1
            if self.delay == 0:
                self.reset()
        else:
            self.life -= 0.3
        
    


count = 0


rewind = 60

rocket_list = []
rocket_list.append(Rocket(400, 400))
rocket_list.append(Rocket(400, 400))
rocket_list.append(Rocket(400, 400))
rocket_list.append(Rocket(400, 400))
rocket_list.append(Rocket(400, 400))
rocket_list.append(Rocket(400, 400))
rocket_list.append(Rocket(400, 400))
rocket_list.append(Rocket(400, 400))
print(rocket_list)



while rewind > 0 :
    
    
    #print(bangcolor)
    #color = np.array((np.asscalar(np.int16(color[0])),np.asscalar(np.int16(color[1])),np.asscalar(np.int16(color[2]))))
    
    #color = tuple(color)
    
    radius = 0

    #cropped_img = bg[min(x):max(y), min(x):max(x)]
    #croppedx = normx*(max(x)-min(x))
    #croppedy = normy*(max(y)-min(y))
    
    #img2 = cv2.imread('dis.jpg')
    
        
    image = np.zeros((400, 400, 3), dtype='uint8')
    
    
    
    #Colored circle
    #print("bang")
    #print(int(bangcolor[0]))
    #print(int(bangcolor[1]))
    #print(int(bangcolor[2]))
    #color = (color[0], color[1], color[2])
    #print(bangcolor)
    for rocket in rocket_list:
        #print(rocket.x)
        rocketrad = int((100-rocket.life)*rocket.scale/5)
        cv2.circle(image, (rocket.x, rocket.y), rocketrad, (int(rocket.b*max(rocket.life-85,0)/100), int(rocket.g*rocket.life*max(rocket.life-85,0)/100), int(rocket.r*rocket.life*max(rocket.life-85,0)/100)), int((rocket.life)/4+25))
        rocket.step()
    
    
    #inner black circle
    #if radius > 100:
        #cv2.circle(image, (200, 200), radius-90, black, -1)
    
    inputimg = image
    img2 = cv2.GaussianBlur(inputimg,(0,0),10,cv2.BORDER_DEFAULT)
    #cv2.imshow("Background", inputimg)
    #cv2.imshow("blur", img2)
    #cv2.waitKey(1)
    wled.image(img2,100)

    
    #time.sleep(1)
    #ret, cur = cam.read()
    #cv2.imshow("Background", cur)
    #cv2.waitKey(1)
    time.sleep(0.0205)
    #duration += 1
        #radius += 1
        #print(radius)
        #print (duration)
    #rewind -= 1