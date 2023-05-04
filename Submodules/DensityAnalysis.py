#!/usr/bin/env python-real

import sys
import os
import numpy as np
from datetime import date
from tools.crop import crop
from tools.writeReport import writeReport
import tools.reader as reader


# Performs analysis on cortical bone
# image: 3D image black and white of bone
# mask: 3D labelmap of bone area, including cavities
# voxSize: The physical side length of the voxels, in mm 
# slope, intercept and scale: parameters of the equation for converting image values to mgHA/ccm
# output: The name of the output directory
def main(inputImg, inputMask, voxSize, slope, intercept, output):
    imgData=reader.readImg(inputImg)
    (maskHeader, maskData) = reader.readMask(inputMask)
    (maskData, imgData) = crop(maskData, imgData)
    density = densityMap(imgData, slope, intercept)

    c = density.shape[2]
    area = np.zeros(c);
    meanDens = np.zeros(c);
    stdDens = np.zeros(c);
    minDens = np.zeros(c);
    maxDens = np.zeros(c);
    # Get stats for each slice
    for sliceNum in range(c):
        sliceDensity = density[:,:,sliceNum]
        maskDensity = sliceDensity[maskData[:,:,sliceNum]]
        area[sliceNum] = len(maskDensity) * voxSize**2
        if(area[sliceNum] != 0):
            meanDens[sliceNum] = np.mean(maskDensity)
            stdDens[sliceNum] = np.std(maskDensity)
            minDens[sliceNum] = np.min(maskDensity)
            maxDens[sliceNum] = np.max(maskDensity)
    # Get average area of all slices
    meanArea = np.mean(area)
    stdArea =  np.std(area)
    minArea = np.min(area)
    maxArea = np.max(area)
    # Get average density of entire bone
    fullDensity = density[maskData]
    meanDensity = np.mean(fullDensity)
    stdDensity = np.std(fullDensity)
    minDensity = np.min(fullDensity)
    maxDensity = np.max(fullDensity)

    fPath = os.path.join(output, "density.txt")

    header = [
        'Date Analyzed',
        'Analysis Path',
        'Area by slice',
        'Mean Density by Slice',
        'Standard Deviation of Density by Slice',
        'Min Density by Slice',
        'Max Density by Slice',
        'Mean Area',
        'Standard Deviation of Area', 
        'Min Area',
        'Max Area',
        'Mean Density',
        'Standard Deviation of Density', 
        'Min Density', 
        'Max Density'
    ]
    data = [
        date.today(),
        fPath,
        area,
        meanDens,
        stdDens,
        minDens,
        maxDens,
        meanArea,
        stdArea,
        minArea,
        maxArea,
        meanDensity,
        stdDensity,
        minDensity,
        maxDensity
    ] 
    writeReport(fPath, header, data)

# Converts an image to a density map the same shape and size
# Uses parameters from DICOM metadata to find linear relationship between pixel value and physical density
def densityMap(img, slope, intercept):
    return img * slope + intercept

if __name__ == "__main__":
    if len(sys.argv) < 7:
        print(sys.argv)
        print("Usage: CancellousAnalysis <input> <mask> <voxelSize> <slope> <intercept> <output>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), str(sys.argv[6]))