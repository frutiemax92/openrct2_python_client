from PIL import Image
from PIL.ImageDraw import floodfill
import numpy as np

def fuzzy_flood(image : Image.Image, threshold):
    upper_pixel = np.array(image.getpixel((0, 0)), dtype=np.float64)
    for y in range(image.height):
        for x in range(image.width):
            color = np.array(image.getpixel((x, y)), dtype=np.float64)

            delta = np.mean(np.abs(color - upper_pixel) / 255.0) * 100.0
            if delta < threshold:
                image.putpixel((x, y), (23, 35, 35))
    return image
    