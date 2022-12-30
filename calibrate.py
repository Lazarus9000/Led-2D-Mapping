import time
import cv2
import os
import requests

#Change these two variables to fit your set up
numberOfLeds = 200
ip = "192.168.1.85
"
white = [255,255,255]
black = [0,0,0]

#Method to write arrays to list, authored by chatGPT 8]
def write_arrays_to_file(list1, list2, filename):
  with open(filename, 'w') as f:
    for i in range(len(list1)):
      f.write(str(list1[i]) + ',' + str(list2[i]) + '\n')

#Method to set all LEDs to a specific color
def allColor(color, count = 0) :
    j = 0
    radiances = []
    while j < count :
        #print(normx[i]
        radiances.append(color)
        j += 1
    r = requests.post('http://' + ip + '/json/state', json={"seg":{"i":radiances}})
    return
    

#Method for setting and individual LED
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

#Method for finding location of LED
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
     

cam = cv2.VideoCapture(0)


#Test that all LEDs light up and tage a background image
allColor(white, numberOfLeds)
time.sleep(0.500)
ret, bg = cam.read()

#Save background image for reference
#img_name = f"./images/bg.png"
#cv2.imwrite(img_name, bg)

cv2.imshow("Background", bg)
cv2.waitKey(1)

#Arrays for holding LED positions
x = []
y = []

for count in range(numberOfLeds):
    #Turn on LED's one at a time
    oneLed(white, count, numberOfLeds)
    
    #For my setup I found that I can't go lower than 0.4 second delay
    #Going lower results in the camera taking pictures of other LED's than the intended oneLed
    #Mileage may vary with different computers, cameras, LED setups, etc.
    time.sleep(0.4) 
    ret, frame = cam.read()
    
    #Uncomment below to save images of individual LEDs - used for initial debugging
    #img_name = f"./images/{count}.png"
    #cv2.imwrite(img_name, frame)
    
    hotSpotPos = findHotSpot(frame, "Background")
    x.append(hotSpotPos[0])
    y.append(hotSpotPos[1])    

write_arrays_to_file(x, y, "calibration.txt")
    