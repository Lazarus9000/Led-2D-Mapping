import time
import cv2
import os
import requests


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
      list1.append(elements[0])
      list2.append(elements[1])

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
cam = cv2.VideoCapture(0)
#Take background picture
allColor(white, numberOfLeds)
time.sleep(0.500)
ret, bg = cam.read()
#img_name = f"./images/bg.png"
#cv2.imwrite(img_name, bg)
cv2.imshow("Background", bg)
cv2.waitKey(1)

# Turn strip on, full brightness
#await led.master( )
count = 0

x = []
y = []

while count < numberOfLeds:
    #print(count)
    oneLed(white, count, numberOfLeds)
    time.sleep(0.4)
    ret, frame = cam.read()
    #img_name = f"./images/{count}.png"
    #cv2.imwrite(img_name, frame)
    hotSpotPos = findHotSpot(frame, "Background")
    x.append(hotSpotPos[0])
    y.append(hotSpotPos[1])    
    count += 1

write_arrays_to_file(x, y, "calibration.txt")
    
normx = normalize(x, 0, 1)
normy = normalize(y, 0, 1)

rewind = 5
while rewind > 0 :
    
    j = 0
    cropped_img = bg[min(x):max(y), min(x):max(x)]
    #croppedx = normx*(max(x)-min(x))
    #croppedy = normy*(max(y)-min(y))
    img2 = cv2.imread('dis.jpg')
    radiances = []
    while j < numberOfLeds :
        coords = [int(normx[j]*img2.shape[0]), int(normy[j]*img2.shape[1])]
        mx = min(int(normy[j]*img2.shape[0]),img2.shape[0]-1)
        my = min(int(normx[j]*img2.shape[1]),img2.shape[1]-1)
        print("x: " + str(mx), " - y: " + str(my))
        color = img2[mx, my]
        print([color[2],color[1],color[0]])
        radiances.append([str(color[2]),str(color[1]),str(color[0])])
        j += 1
    r = requests.post('http://' + ip + '/json/state', json={"seg":{"i":radiances}})
    time.sleep(1)
    ret, cur = cam.read()
    cv2.imshow("Background", cur)
    cv2.waitKey(1)
    time.sleep(15)
        
    i = 0
    while i < 1500 :
        
        j = 0
        radiances = []
        while j < numberOfLeds :
            #print(normx[i]
            distance = abs(i-x[j])
            radiance = min(255*(distance/250),255)
            #if(j == 20) :
            #    print(str(x[j]) + " " + str(distance) + " " + str(radiance))
            radiances.append([radiance,radiance,radiance])
            j += 1
        
        #Draw imaginary line
        #newbg = bg.copy()
        ret, cur = cam.read()
        cv2.line(cur, [i,0], [i,bg.shape[0]],[255,255,255],1)
        #cv2.circle(cur, (x[20],y[20]), 25, (255, 0, 0), 2)
        cv2.imshow("Background", cur)
        
        
        ret, cur = cam.read()
        #cv2.imshow("Live", cur)
        cv2.waitKey(1)
        r = requests.post('http://' + ip + '/json/state', json={"seg":{"i":radiances}})
        i += 10
        time.sleep(0.005)
        
    i = -250
    while i < 1000 :
        
        j = 0
        radiances = []
        while j < numberOfLeds :
            #print(normx[i]
            distance = abs(i-y[j])
            radiance = min(255*(distance/1000),255)
            #if(j == 20) :
            #    print(str(x[j]) + " " + str(distance) + " " + str(radiance))
            radiances.append([radiance,radiance,radiance])
            j += 1
        
        #Draw imaginary line
        #newbg = bg.copy()
        ret, cur = cam.read()
        cv2.line(cur, [0,i], [bg.shape[1],i],[255,255,255],1)
        #cv2.circle(cur, (x[20],y[20]), 25, (255, 0, 0), 2)
        cv2.imshow("Background", cur)
        
        
        ret, cur = cam.read()
        #cv2.imshow("Live", cur)
        cv2.waitKey(1)
        r = requests.post('http://' + ip + '/json/state', json={"seg":{"i":radiances}})
        i += 10
        time.sleep(0.005)
    
    rewind -= 1