import time
import cv2
import os

#Initiate wledMapper
wled = Mapper("192.168.1.172", 450, "UDP", "")

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
     
#Change number in videocapture if more than one camera is connected to system
cam = cv2.VideoCapture(0)


#Test that all LEDs light up and tage a background image
wled.allColor(wled.white, wled.numberOfLeds)
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
    wled.oneLed(wled.white, count, wled.numberOfLeds)
    
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