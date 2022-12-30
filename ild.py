import cv2
from noise import perlin
import numpy as np

def generate_perlin_noise_image(width, height, scale=100):
    # Create an empty image with the given size
    image = np.zeros((height, width, 3), dtype=np.uint8)

    # Generate Perlin noise for each pixel in the image
    for y in range(height):
        for x in range(width):
            # Generate a noise value in the range [0, 1]
            noise = perlin(x / scale, y / scale)
            # Scale the noise value to the range [0, 255] and assign it to the pixel
            image[y, x] = ((noise + 1) * 128).astype(np.uint8)
    
    return image

# Generate a Perlin noise image of size 512x512 and save it to a file
image = generate_perlin_noise_image(512, 512)
# Display the noise image using cv2
cv2.imshow("Perlin Noise", image)
cv2.waitKey(0)
