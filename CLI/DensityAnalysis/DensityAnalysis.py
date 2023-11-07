#!/usr/bin/env python-real

import sys
import os
import numpy as np
from datetime import date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MusculoskeletalAnalysisCLITools.crop import crop
from MusculoskeletalAnalysisCLITools.writeReport import writeReport
from MusculoskeletalAnalysisCLITools.density import densityMap
import MusculoskeletalAnalysisCLITools.reader as reader


# Performs analysis on cortical bone
# image: 3D image black and white of bone
# mask: 3D labelmap of bone area, including cavities
# voxSize: The physical side length of the voxels, in mm
# slope, intercept and scale: parameters of the equation for converting image values to mgHA/ccm
# output: The name of the output directory
def main(inputImg, inputMask, voxSize, slope, intercept, name, output):
    imgData=reader.readImg(inputImg)
    (_, maskData) = reader.readMask(inputMask)
    (maskData, imgData) = crop(maskData, imgData)
    if np.count_nonzero(maskData) == 0:
         raise Exception("Segmentation mask is empty.")
    density = densityMap(imgData, slope, intercept)

    c = density.shape[2]
    area = np.zeros(c);
    meanDens = np.zeros(c);
    stdDens = np.zeros(c);
    minDens = np.zeros(c);
    maxDens = np.zeros(c);
    print("""<filter-progress>{}</filter-progress>""".format(.25))
    sys.stdout.flush()
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
    print("""<filter-progress>{}</filter-progress>""".format(.50))
    sys.stdout.flush()
    # Get average area of all slices
    meanArea = np.mean(area)
    stdArea =  np.std(area)
    minArea = np.min(area)
    maxArea = np.max(area)
    print("""<filter-progress>{}</filter-progress>""".format(.75))
    sys.stdout.flush()
    # Get average density of entire bone
    fullDensity = density[maskData]
    meanDensity = np.mean(fullDensity)
    stdDensity = np.std(fullDensity)
    minDensity = np.min(fullDensity)
    maxDensity = np.max(fullDensity)

    fPath = os.path.join(output, "density.txt")

    header = [
        'Date Analysis Performed',
        'Input Volume',
        'Area by Slice',
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
        name,
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



if __name__ == "__main__":
    if len(sys.argv) < 8:
        print(sys.argv)
        print("Usage: CancellousAnalysis <input> <mask> <voxelSize> <slope> <intercept> <name> <output>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), str(sys.argv[6]), str(sys.argv[7]))