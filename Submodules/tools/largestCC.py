import numpy as np
try:
    from skimage.measure import label
except:
    from slicer.util import pip_install
    pip_install("scikit-image")
    from skimage.measure import label

# Takes a binary numpy array
# Finds the largest connected component 
# Returns the mask with only the largest component
def largestCC(mask):
    labels = label(mask)
    largest = labels == np.argmax(np.bincount(labels[np.nonzero(labels)]))
    if np.count_nonzero(largest) == 0:
        raise Exception("Largest connected component not found")
    return largest
