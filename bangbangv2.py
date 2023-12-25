import time
import cv2
import os

import numpy as np
import random
import colorsys
import socket


#Change these two variables to fit your set up
numberOfLeds = 450
ip = "192.168.1.172"
WLED_PORT = 21324
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
protocol = 2
timeout = 1
white = (255,255,255)
black = (0,0,0)

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
        
    

def write_arrays_to_file(list1, list2, filename):
  with open(filename, 'w') as f:
    for i in range(len(list1)):
      f.write(str(list1[i]) + ',' + str(list2[i]) + '\n')

def read_arrays_from_file(filename):
  list1 = []
  list2 = []

  with open(filename, 'r') as f:
    for line in f:
      elements = line.strip().split(',')
      list1.append(int(elements[0]))
      list2.append(int(elements[1]))

  return list1, list2

#Method to set all LEDs to a specific color
def allColor(color, count = 0) :
    j = 0
    
    data = bytearray([protocol, timeout])
    while j < count :
        #print(normx[i]
        data += bytearray([color[0], color[1], color[2]])
        
        j += 1
    data[1] = 255
    sock.sendto(data, (ip, WLED_PORT))
    #print(data, (ip, WLED_PORT))
    return
    

#Method for setting and individual LED
def oneLed(color, index = 0,  count = 0) :
    j = 0
    data = bytearray([protocol, timeout])
    while j < count :
        #print(normx[i]
        if(index == j) :
            data += bytearray([color[0], color[1], color[2]])
        else:
            data += bytearray([0, 0, 0])
            
        j += 1
    data[1] = 255
    sock.sendto(data, (ip, WLED_PORT))
    #print(data, (ip, WLED_PORT))
    return

def findHotSpot(image, window) :
    orig = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # apply a Gaussian blur to the image then find the brightest
    # region
    gray = cv2.GaussianBlur(gray, (25, 25), 0)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
    image = orig.copy()
    cv2.circle(image, maxLoc, 25, (255, 0, 0), 2)
    # display the results of our newly improved method
    
    cv2.imshow(window, image)
    cv2.waitKey(1)
    return(maxLoc)
     

# explicit function to normalize array
def normalize(arr, t_min, t_max):
    norm_arr = []
    diff = t_max - t_min
    diff_arr = max(arr) - min(arr)
    for i in arr:
        temp = (((i - min(arr))*diff)/diff_arr) + t_min
        norm_arr.append(temp)
    return norm_arr

#main program
absolute_path = os.path.dirname(__file__)
imgpath = os.path.join(absolute_path, "images")
#cam = cv2.VideoCapture(0)
#Take background picture
allColor(white, numberOfLeds)
#time.sleep(0.500)
#ret, bg = cam.read()
#img_name = f"./images/bg.png"
#cv2.imwrite(img_name, bg)
#cv2.imshow("Background", bg)
#cv2.waitKey(1)

# Turn strip on, full brightness
#await led.master( )
count = 0

x = []
y = []

#while count < numberOfLeds:
    #print(count)
    #oneLed(white, count, numberOfLeds)
    #time.sleep(0.4)
    #ret, frame = cam.read()
    #img_name = f"./images/{count}.png"
    #cv2.imwrite(img_name, frame)
    #hotSpotPos = findHotSpot(frame, "Background")
    #x.append(hotSpotPos[0])
    #y.append(hotSpotPos[1])    
    #count += 1

#write_arrays_to_file(x, y, "calibration.txt")
x,y = read_arrays_from_file("calibrationfixed.txt")
    
normx = normalize(x, 0, 1)
normy = normalize(y, 0, 1)

rewind = 60

rocket_list = []
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
    cv2.imshow("Background", inputimg)
    cv2.imshow("blur", img2)
    cv2.waitKey(1)
    data = bytearray([protocol, timeout])
    
    for j in range(numberOfLeds) :
        mx = max(min(int(normy[j]*img2.shape[0]),img2.shape[0]-1),0)
        my = max(min(int(normx[j]*img2.shape[1]),img2.shape[1]-1),0)
        #print("x: " + str(mx), " - y: " + str(my))
        color = img2[mx, my]
        #color[0] = int(color[0]**3/255**2)
        #color[1] = int(color[1]**3/255**2)
        #color[2] = int(color[2]**3/255**2)
        #print([color[2],color[1],color[0]])
        #radiances.append([str(color[2]),str(color[1]),str(color[0])])
        data += bytearray([color[2], color[1], color[0]])
            
    data[1] = 255
    sock.sendto(data, (ip, WLED_PORT))
    
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