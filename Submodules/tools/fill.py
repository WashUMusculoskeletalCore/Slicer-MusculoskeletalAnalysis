import skimage.morphology
import numpy as np

# Takes a 2D binary numpy array and an integer radius
# Performs morphological close with the given radius, then fills any holes not connected to the outer edge
# Returns the transformed array
def fill(mask, radius):

    # Performs morphological close, filling small gaps
    strel = skimage.morphology.disk(radius, dtype='bool')
    skimage.morphology.binary_closing(mask, footprint=strel, out=mask)

    # Fills in all holes not connected to the edges
    seed = np.ones_like(mask, dtype='bool')

    seed[0,:] = mask[0,:]
    seed[-1,:] = mask[-1,:]   
    seed[:,-1] = mask[:,-1]
    seed[:,0] = mask[:,0]
    mask = skimage.morphology.reconstruction(seed, mask, method='erosion')
    return mask
