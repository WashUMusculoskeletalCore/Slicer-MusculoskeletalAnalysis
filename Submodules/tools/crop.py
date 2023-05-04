import numpy as np

# Crops a series of ndarrays to the range of nonzero values in the first array for each dimension
def crop(*args):
    template = args[0]
    coords = np.nonzero(template)
    sliceC = ()
    for c in coords:
        sliceC += slice(min(c),max(c)+1),
    croppedArgs = ()
    for a in args:
        croppedArgs += a[sliceC],
    return croppedArgs