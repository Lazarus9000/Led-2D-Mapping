import time
import cv2
import os
import requests
import numpy as np


class Snow:
    def __init__(self, var1, var2, var3):
        self.x = var1
        self.y = var2
        self.speed = var3

numberOfLeds = 200
ip = "192.168.1.85"
white = [255,255,255]
black = [0,0,0]

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

def allColor(color, count = 0) :
    j = 0
    radiances = []
    while j < count :
        #print(normx[i]
        radiances.append(color)
        j += 1
    r = requests.post('http://' + ip + '/json/state', json={"seg":{"i":radiances}})
    return
    

def oneLed(color, index = 0,  count = 0) :
    j = 0
    radiances = []
    while j < count :
        #print(normx[i]
        if(index == j) :
            radiances.append(color)
        else:
            radiances.append(black)
            
        j += 1
    r = requests.post('http://' + ip + '/json/state', json={"seg":{"i":radiances}})
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
x,y = read_arrays_from_file("calibration.txt")
    
normx = normalize(x, 0, 1)
normy = normalize(y, 0, 1)

snow_list = []
snow_list.append(Snow(50, -1, 5))
snow_list.append(Snow(150, -100, 5))
snow_list.append(Snow(250, 100, 5))
snow_list.append(Snow(350, 500, 5))
snow_list.append(Snow(100, 250, 5))
snow_list.append(Snow(300, -200, 5))

rewind = 60


while rewind > 0 :
    
    j = 0
    #cropped_img = bg[min(x):max(y), min(x):max(x)]
    #croppedx = normx*(max(x)-min(x))
    #croppedy = normy*(max(y)-min(y))
    
    #img2 = cv2.imread('dis.jpg')
    image = np.zeros((400, 400, 3), dtype='uint8')
    
    for snow in snow_list:
        snow.y = snow.y+snow.speed
        if snow.y > image.shape[1] + 100:
            snow.y = snow.y - image.shape[1] - 200
        cv2.circle(image, (snow.x,snow.y), 25, (255, 255, 255), -1)
    
    
    
    inputimg = image
    img2 = cv2.GaussianBlur(inputimg,(0,0),10,cv2.BORDER_DEFAULT)
    #cv2.imshow("Background", inputimg)
    #cv2.imshow("blur", img2)
    #cv2.waitKey(1)
    radiances = []
    
    width = int(img2.shape[1])
    for j in range(numberOfLeds) :
        mx = max(min(int(normy[j]*img2.shape[0]),img2.shape[0]-1),0)
        my = max(min(int(normx[j]*img2.shape[1]),img2.shape[1]-1),0)
        #print("x: " + str(mx), " - y: " + str(my))
        color = img2[mx, my]
        #color[0] = int(color[0]**3/255**2)
        #color[1] = int(color[1]**3/255**2)
        #color[2] = int(color[2]**3/255**2)
        #print([color[2],color[1],color[0]])
        radiances.append([str(color[2]),str(color[1]),str(color[0])])
            
    r = requests.post('http://' + ip + '/json/state', json={"seg":{"i":radiances}})
    
    #time.sleep(1)
    #ret, cur = cam.read()
    #cv2.imshow("Background", cur)
    #cv2.waitKey(1)
    time.sleep(0.0105)
        
    #rewind -= 1