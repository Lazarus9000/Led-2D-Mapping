import socket
import requests

class Mapper:

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

    white = [255,255,255]
    black = [0,0,0]

    def __init__(self, newip, Leds, newprotocol, calibrationfile):
        if calibrationfile != "":
            tx,ty = self.read_arrays_from_file(calibrationfile)
            self.x.extend(tx)
            self.y.extend(ty)
            self.normx.extend(self.normalize(self.x, 0, 1))
            self.normy.extend(self.normalize(self.y, 0, 1))

        self.ip = "192.168.1.172"
        self.numberOfLeds = Leds
        self.protocol = newprotocol

        if self.protocol == "UDP":
            global sock
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            


    #Utility function to normalize array
    def normalize(self, arr, t_min, t_max):
        norm_arr = []
        diff = t_max - t_min
        diff_arr = max(arr) - min(arr)
        for i in arr:
            temp = (((i - min(arr))*diff)/diff_arr) + t_min
            norm_arr.append(temp)
        return norm_arr

    #Utility function to write calibration data
    def write_arrays_to_file(self, list1, list2, filename):
      with open(filename, 'w') as f:
        for i in range(len(list1)):
          f.write(str(list1[i]) + ',' + str(list2[i]) + '\n')



    #Utility function to read calibration data
    def read_arrays_from_file(self, filename):
      list1 = []
      list2 = []

      with open(filename, 'r') as f:
        for line in f:
          elements = line.strip().split(',')
          list1.append(int(elements[0]))
          list2.append(int(elements[1]))

      return list1, list2

    def allColor(self, color, count = 0):
        j = 0
        radiances = []
        while j < count :
            #print(normx[i]
            radiances.append(color)
            j += 1
        self.colors(radiances)
        return
        

    def oneLed(self, color, index = 0,  count = 0):
        j = 0
        radiances = []
        while j < count :
            #print(normx[i]
            if(index == j) :
                radiances.append(color)
            else:
                radiances.append(black)
                
            j += 1
        self.colors(radiances)
        return

    def colors(self, colors):
        if self.protocol == "JSON":
            r = requests.post('http://' + self.ip + '/json/state', json={"seg":{"i":colors}})
            
        
        if self.protocol == "UDP":
            data = bytearray([self.udpProtocol, self.udpTimeout])
            for color in colors:
                data += bytearray([color[2], color[1], color[0]])
            
            data[1] = 255
            self.sock.sendto(data, (self.ip, self.WLED_PORT))

    def image(self, img, brightness):
        pixels = []
        for j in range(self.numberOfLeds) :
            #map from image to leds
            mx = max(min(int(self.normy[j]*img.shape[0]),img.shape[0]-1),0)
            my = max(min(int(self.normx[j]*img.shape[1]),img.shape[1]-1),0)
            color = img[mx, my]
            color[0] = color[0]*(brightness/100)
            color[1] = color[1]*(brightness/100)
            color[2] = color[2]*(brightness/100)
            pixels.append(color)
            
        
        self.colors(pixels)
