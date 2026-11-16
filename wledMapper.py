import socket
import sys
import requests

#Preview window
#Start any script with --preview to see the picture that is sent to the LEDs in a window
#on the computer, e.g. "python rotator.py image2.jpg --preview". Without it (or with
#--no-preview) no window is opened, which is what you want on a server without a screen
previewEnabled = "--preview" in sys.argv and "--no-preview" not in sys.argv

#Show img in a window called name, but only when the script was started with --preview
def preview(name, img):
    if previewEnabled:
        import cv2
        cv2.imshow(name, img)
        cv2.waitKey(1)

#The command line arguments of the script, without the preview switches
def arguments():
    return [a for a in sys.argv[1:] if a not in ("--preview", "--no-preview")]

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

        self.ip = newip
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
                radiances.append(self.black)

            j += 1
        self.colors(radiances)
        return

    #Hand control back to WLED. The realtime packets sent by colors() never time out,
    #so without this the chain stays frozen until WLED is restarted or gets new data
    def release(self):
        if self.protocol == "UDP":
            self.sendUdp([self.black] * self.numberOfLeds, 1)
            #WLED ignores a shorter timeout once "no timeout" has been set, so ask it
            #to leave realtime mode through the JSON API as well
            try:
                requests.post('http://' + self.ip + '/json/state', json={"live": False}, timeout=5)
            except requests.RequestException:
                print("Could not reach WLED to end realtime mode - restart it or send {\"live\":false} to /json/state")

    def colors(self, colors):
        if self.protocol == "JSON":
            r = requests.post('http://' + self.ip + '/json/state', json={"seg":{"i":colors}})
            
        
        if self.protocol == "UDP":
            self.sendUdp(colors, 255)

    #Send colors (BGR order, as in OpenCV images) as WLED realtime UDP
    #Up to 490 LEDs fit in one DRGB packet. Longer chains are split over several DNRGB
    #packets, which carry the index of their first LED and hold 489 LEDs each
    def sendUdp(self, colors, timeout):
        if len(colors) <= 490:
            data = bytearray([self.udpProtocol, timeout])
            for color in colors:
                data += bytearray([int(color[2]), int(color[1]), int(color[0])])
            self.sock.sendto(data, (self.ip, self.WLED_PORT))
            return
        for start in range(0, len(colors), 489):
            data = bytearray([4, timeout, start >> 8, start & 255])
            for color in colors[start:start + 489]:
                data += bytearray([int(color[2]), int(color[1]), int(color[0])])
            self.sock.sendto(data, (self.ip, self.WLED_PORT))

    def image(self, img, brightness):
        pixels = []
        for j in range(self.numberOfLeds) :
            #map from image to leds
            mx = max(min(int(self.normy[j]*img.shape[0]),img.shape[0]-1),0)
            my = max(min(int(self.normx[j]*img.shape[1]),img.shape[1]-1),0)
            #copy, otherwise the brightness scaling below darkens the picture itself and
            #a second LED that reads the same pixel comes out dimmer
            color = img[mx, my].copy()
            color[0] = color[0]*(brightness/100)
            color[1] = color[1]*(brightness/100)
            color[2] = color[2]*(brightness/100)
            pixels.append(color)
            
        
        self.colors(pixels)
