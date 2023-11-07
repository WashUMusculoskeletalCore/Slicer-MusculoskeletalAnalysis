import numpy as np
from skimage.measure import label

# Takes a binary numpy array
# Finds the largest connected component
# Returns the mask with only the largest component
def largestCC(mask):
    # Creates a labelmap of the mask, where connected components have the same label
    labels = label(mask)
    # labels[np.nonzero(labels)] is a list of all nonzero values in the labelmap. np.argmax(np.bincount()) returns the most common number in that list. largest is set to a mask showing where the labelmap is equal to that value.
    largest = labels == np.argmax(np.bincount(labels[np.nonzero(labels)]))
    if np.count_nonzero(largest) == 0:
        # Throw an exception if the output mask is empty. This could happen if the input mask is also empty
        raise Exception("Largest connected component not found")
    return largest
