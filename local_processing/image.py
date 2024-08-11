import numpy as np
from PIL import Image

stillCount = 0

# Function to check if screen has stopped moving for a certain amount of time (counts) 
def imageChange(image: Image.Image) -> bool:
    global prevImage, stillCount
    if stillCount == 4: # counted every 0.2 seconds
        stillCount += 1
        return True
    else:
        image = np.array(image)
        if stillCount == 0:
            prevImage = np.array(image)
        if (image.shape == prevImage.shape) and similarityScore(image, prevImage) > 0.95:
            stillCount += 1
        else:
            stillCount = 0
        return False

# Calculate the similarity between 2 images by pixel (percentage represented as float [0, 1])
def similarityScore(arr1, arr2) -> float: 
    comparison = arr1 == arr2
    matching_elements = np.sum(comparison)
    similarity = matching_elements / np.prod(arr1.shape)
    return similarity