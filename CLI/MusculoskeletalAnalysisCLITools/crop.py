import numpy as np

def crop(*args):
    """Crops a series of ndarrays to the range of nonzero values in the first array for each dimension."""
    template = args[0]
    # Get the coodinates of all nonzero points in the first input as a tuple of arrays
    coords = np.nonzero(template)
    sliceC = ()
    # For each dimension, get a slice from the smallest to largest values
    for i, c in enumerate(coords):
        low = min(c)
        high = max(c)+1
        # Leave 1 space between shape and new edge unless the shape was already on the edge
        if low > 0:
            low==low-1
        if high < np.shape(template)[i]:
            high = high+1
        sliceC += slice(low , high),
    croppedArgs = ()
    # For each input, apply the slice and return the results
    for a in args:
        croppedArgs += a[sliceC],
    return croppedArgs