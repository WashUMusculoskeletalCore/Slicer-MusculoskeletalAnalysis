# Calculates thickness by finding the largest sphere containing each point

def findSpheres(mask):
    import numpy as np
    from math import ceil
    from scipy.ndimage import distance_transform_edt

    dist = distance_transform_edt(mask)
    rads = dist.copy()

    a,b,c=np.nonzero(mask)
    order = np.argsort(dist[a,b,c])
    
    for n in order:
        # For each point, find the thickness radius at that point from the distance map
        x=a[n]
        y=b[n]
        z=c[n]

        r=dist[x,y,z]
        # Equivalent to floor, except it reduces integers by 1, gives the maximum chessboard distance to any point less than radius
        rf = ceil(r-1)
        # Check that ranges are inside boundaries
        xr0=min(rf,x)
        xr1=min(rf, dist.shape[0]-x-1)
        yr0=min(rf,y)
        yr1=min(rf, dist.shape[1]-y-1)
        zr0=min(rf,z)
        zr1=min(rf, dist.shape[2]-z-1)
        # Creates a cubic view of the region of interest
        roi=rads[x-xr0:x+xr1+1, y-yr0:y+yr1+1, z-zr0:z+zr1+1]
        # Creates mask of sphere within radius
        i,j,k=np.mgrid[-xr0:xr1+1,-yr0:yr1+1,-zr0:zr1+1]
        mask = (i**2 + j**2 + k**2 < r**2)
        mask = np.bitwise_and(mask, roi>0)
        # Sets all values inside region of interest and sphere mask to the radius if it is higher than their current value
        mask = mask * r
        roi[:,:,:] = np.maximum(roi, mask)
    return rads[np.nonzero(rads)]
