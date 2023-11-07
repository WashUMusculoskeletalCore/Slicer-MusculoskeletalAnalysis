# Calculates the width of a 2d shape using rotating calipers method
import math
from scipy.ndimage import convolve
import numpy as np

def crossProduct(a,b,c):
    return ((b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]))

# Finds the points on the convex hull
# Prereq: The points must be sorted left to right and top to bottom
def convexHull(pts):

    hull = []
    n = len(pts)
    # Add points from left to right, remove any that make a clockwise turn
    for p in pts:
        while len(hull) >= 2 and crossProduct(hull[-2], hull[-1], p) <= 0:
            hull.pop()
        hull.append(p)
    # Repeat from right to left to fill out the bottom of the hull
    for p in pts[n-2:-1:-1]:
        while len(hull) >= 2 and crossProduct(hull[-2], hull[-1], p) <= 0:
            hull.pop()
        hull.append(p)
    # Exclude the last point because it is same as the first
    return hull[:-1]

def rotatingCaliper(pts):
    hull = convexHull(pts)
    n = len(hull)

    if n <= 1:
        return 0
    if n == 2:
        return math.sqrt((hull[0][0]-hull[1][0])**2+(hull[1][0]-hull[1][1])**2)
    k = 1
    # Find the furthest point
    while crossProduct(hull[n - 1], hull[0], hull[(k + 1) % n]) > crossProduct(hull[n - 1], hull[0], hull[k]):
        k += 1

    res = 0

    # For each point between 0 and k find the opposite point j
    for i in range(k + 1):
        j = (i + 1) % n
        while crossProduct(hull[i], hull[(i + 1) % n], hull[(j + 1) % n]) > crossProduct(hull[i], hull[(i + 1) % n], hull[j]):
            j = (j + 1) % n
            res = max(res, math.sqrt((hull[i][0]-hull[j][0])**2+(hull[i][0]-hull[j][1])**2))

    return res

def edge(img):
    filt = [[0,-1,0],
              [-1,4,-1],
              [0,-1,0]]
    return np.argwhere(convolve(img ,filt, mode='constant') >= 1)


def width(mask):
    n = mask.shape[2]
    maxw = 0
    for i in range(n):
        pts = edge(mask[:,:,i])
        w = rotatingCaliper(pts)
        maxw = max(maxw, w)
    return maxw