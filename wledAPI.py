import socket
import requests

numberOfLeds = 200
ip = "192.168.1.172"

#https://kno.wled.ge/interfaces/udp-realtime/
protocol = "JSON"

#Valid values: "JSON", "UDP"
#Not sure JSON is able to handle more than 250 individual leds

#UDP implementation based on https://github.com/RolandDaum/WLED-UDP-Realtime-Controll-Python-JavaScript/blob/master/WLEDUDP.py
#Maybe implement UDP variables as settings as well later
WLED_PORT = 21324
sock = ""
udpProtocol = 2
#2 = DRGB - max leds 490
udpTimeout = 1

x = []
y = []
normx = []
normy = []

def wled(newip, Leds, newprotocol, calibrationfile):
    tx,ty = read_arrays_from_file(calibrationfile)
    x.extend(tx)
    y.extend(ty)
    normx.extend(normalize(x, 0, 1))
    normy.extend(normalize(y, 0, 1))

    global ip
    ip = "192.168.1.172"
    global numberOfLeds
    numberOfLeds = Leds
    global protocol
    protocol = newprotocol

    if protocol == "UDP":
        global sock
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
white = [255,255,255]
black = [0,0,0]

#Utility function to normalize array
def normalize(arr, t_min, t_max):
    norm_arr = []
    diff = t_max - t_min
    diff_arr = max(arr) - min(arr)
    for i in arr:
        temp = (((i - min(arr))*diff)/diff_arr) + t_min
        norm_arr.append(temp)
    return norm_arr

#Utility function to write calibration data
def write_arrays_to_file(list1, list2, filename):
  with open(filename, 'w') as f:
    for i in range(len(list1)):
      f.write(str(list1[i]) + ',' + str(list2[i]) + '\n')



#Utility function to read calibration data
def read_arrays_from_file(filename):
  list1 = []
  list2 = []

  with open(filename, 'r') as f:
    for line in f:
      elements = line.strip().split(',')
      list1.append(int(elements[0]))
      list2.append(int(elements[1]))

  return list1, list2

def allColor(color, count = 0):
    j = 0
    radiances = []
    while j < count :
        #print(normx[i]
        radiances.append(color)
        j += 1
    colors(radiances)
    return
    

def oneLed(color, index = 0,  count = 0):
    j = 0
    radiances = []
    while j < count :
        #print(normx[i]
        if(index == j) :
            radiances.append(color)
        else:
            radiances.append(black)
            
        j += 1
    colors(radiances)
    return

def colors(colors):
    if protocol == "JSON":
        r = requests.post('http://' + ip + '/json/state', json={"seg":{"i":colors}})
        
    
    if protocol == "UDP":
        data = bytearray([udpProtocol, udpTimeout])
        for color in colors:
            data += bytearray([color[2], color[1], color[0]])
        
        data[1] = 255
        sock.sendto(data, (ip, WLED_PORT))

def image(img, brightness):
    pixels = []
    for j in range(numberOfLeds) :
        #map from image to leds
        mx = max(min(int(normy[j]*img.shape[0]),img.shape[0]-1),0)
        my = max(min(int(normx[j]*img.shape[1]),img.shape[1]-1),0)
        color = img[mx, my]
        color[0] = color[0]*(100/brightness)
        color[1] = color[1]*(100/brightness)
        color[2] = color[2]*(100/brightness)
        pixels.append(color)
        
    
    colors(pixels)
