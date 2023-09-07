import numpy as np

# Crops a series of ndarrays to the range of nonzero values in the first array for each dimension
def crop(*args):
    template = args[0]
    # Get the coodinates of all nonzero points in the first input as a tuple of arrays
    coords = np.nonzero(template)
    sliceC = ()
    # For each dimension, get a slice from the smallest to largest values
    for c in coords:
        sliceC += slice(min(c),max(c)+1),
    croppedArgs = ()
    # For each input, apply the slice and return the results
    for a in args:
        croppedArgs += a[sliceC],
    return croppedArgs