import numpy as np
from matplotlib.colors import hsv_to_rgb
import noise
import cv2
import time
import requests

def read_arrays_from_file(filename):
  list1 = []
  list2 = []

  with open(filename, 'r') as f:
    for line in f:
      elements = line.strip().split(',')
      list1.append(int(elements[0]))
      list2.append(int(elements[1]))

  return list1, list2
  
# explicit function to normalize array
def normalize(arr, t_min, t_max):
    norm_arr = []
    diff = t_max - t_min
    diff_arr = max(arr) - min(arr)
    for i in arr:
        temp = (((i - min(arr))*diff)/diff_arr) + t_min
        norm_arr.append(temp)
    return norm_arr

numberOfLeds = 200
ip = "192.168.1.85"

x = []
y = []
x,y = read_arrays_from_file("calibration.txt")
normx = normalize(x, 0, 1)
normy = normalize(y, 0, 1)

# Create a vectorized version of the pnoise3 function
vec_pnoise3 = np.vectorize(noise.pnoise3)

# Create a figure and axes
#fig, ax = plt.subplots()

# Initialize the noise array
noise_values = np.zeros((100, 100))

# Create the x and y coordinate arrays using the NumPy meshgrid function
x, y = np.meshgrid(range(100), range(100))

# Create the hue, saturation, and value arrays
hue = np.zeros((100, 100))
saturation = np.zeros((100, 100))
value = np.zeros((100, 100))

# Define the minimum and maximum hue values for the gradient
hue_min = 0.0
hue_max = 0.16
gradient_ratio = 0.7

# Function to update the plot at each frame
def update(frame):
    global noise_values

    # Generate new noise values using the x and y coordinate arrays
    noise_values = vec_pnoise3(x / 30, y / 30 + frame * 2, frame)

    # Adjust the range of the noise values to the range 0-1
    noise_values = (noise_values - np.min(noise_values)) / (np.max(noise_values) - np.min(noise_values))

    # Use the y coordinate of each pixel as the hue value
    hue[:, :] = y / 100

    # Add the gradient hue values to the noise hue values
    hue[:, :] = (hue[:, :] * gradient_ratio) + (noise_values * (1 - gradient_ratio))
    # Scale and shift the hue values using the hue_min and hue_max variables
    hue[:, :] = hue[:, :] * (hue_max - hue_min) + hue_min

    # Make the saturation and value relative to the hue value
    saturation_ratio = 0.1
    saturation[:, :] = saturation_ratio + (hue[:, :] / hue_max) * (1 - saturation_ratio)
    saturation[:, :] = 1 - saturation[:, :]
    value_ratio = 0.3
    value[:, :] = value_ratio + hue[:, :] / hue_max * (1 - value_ratio)

    # Adjust the saturation by multiplying by a constant value
    #saturation[:, :] = np.ones_like(hue[:, :]) * 1

    # Adjust the value by multiplying by a constant value
    #value[:, :] = np.ones_like(hue[:, :]) * 1

    # Convert the hue, saturation, and value arrays to RGB colors
    rgb = hsv_to_rgb(np.dstack((hue, saturation, value)))

    # Set the image data and redraw the plot
    #ax.imshow(rgb)
    image = rgb[:, :, ::-1]
    cv2.imshow("blur", image)
    cv2.waitKey(1)
    
    radiances = []
    
    for j in range(numberOfLeds) :
        mx = max(min(int(normy[j]*image.shape[0]),image.shape[0]-1),0)
        my = max(min(int(normx[j]*image.shape[1]),image.shape[1]-1),0)
        #print("x: " + str(mx), " - y: " + str(my))
        color = image[mx, my]
        color[0] = int(color[0]*255)
        color[1] = int(color[1]*255)
        color[2] = int(color[2]*255)
        #print([color[2],color[1],color[0]])
        radiances.append([str(color[2]),str(color[1]),str(color[0])])
            
    r = requests.post('http://' + ip + '/json/state', json={"seg":{"i":radiances}})


# Create the animation using the update function

while 1 > 0:
    frames=np.linspace(0, 10, 100)
    #print(frames)
    for frame in frames:
        update(frame)
        time.sleep(0.05)

#anim = animation.FuncAnimation(fig, update, frames=np.linspace(0, 10, 100), interval=50)
#anim.save('basic_animation.mp4',  extra_args=['-vcodec', 'libx264'])
#plt.show()
