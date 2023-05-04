import numpy as np
from skimage.measure import label

# Takes a binary numpy array
# Finds the largest connected component 
# Returns the mask with only the largest component
def largestCC(mask):
    labels = label(mask)
    largest = labels == np.argmax(np.bincount(labels.flat[1:]))+1
    return largest
