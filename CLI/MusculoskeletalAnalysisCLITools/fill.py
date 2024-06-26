

def fill(mask, radius):
    """Performs morphological close with the given radius, then fills any holes not connected to the outer edge.

    Takes a 2D binary numpy array and an integer radius.

    Returns the transformed array.
    """
    import numpy as np
    import skimage.morphology
    # Performs morphological close, filling small gaps
    strel = skimage.morphology.disk(radius, dtype='bool')
    # Pad image to remove edge related problems
    mask=np.pad(mask, radius, mode='constant', constant_values=0)
    skimage.morphology.binary_closing(mask, footprint=strel, out=mask)
    mask=mask[radius:-radius, radius:-radius]
    # Fills in all holes not connected to the edges
    seed = np.ones_like(mask, dtype='bool')

    # seed is a mask of all ones, except zero where mask has zeros on the edges
    seed[0,:] = mask[0,:]
    seed[-1,:] = mask[-1,:]
    seed[:,-1] = mask[:,-1]
    seed[:,0] = mask[:,0]
    # seed's zero areas are expanded to match mask's zeros
    mask = skimage.morphology.reconstruction(seed, mask, method='erosion')
    return mask
