#!/usr/bin/env python-real

import sys
import os
from datetime import date

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MusculoskeletalAnalysisCLITools import (
  crop,
  densityMap,
  readImg,
  readMask,
  writeReport,
)


OUTPUT_FIELDS = [
    ("Date Analysis Performed", "The current date"),
    ("Input Volume", "Name of the input volume"),
    ("Area by Slice", "The area of the segment in each slice of each slice"),
    ("Mean Density by Slice", "The average density of the segmented area each slice"),
    ("Standard Deviation of Density by Slice", "The standard deviation of the density of each slice"),
    ("Min Density by Slice", "The lowest density in the segment of each slice"),
    ("Max Density by Slice", "The highest density in the segment of each slice"),
    ("Mean Area", "The mean area of the segment of all slices"),
    ("Standard Deviation of Area", "The standard deviation of the segmented area of all slices"),
    ("Min Area", "The area of the smallest segment slice"),
    ("Max Area", "The area of the largest segment slice"),
    ("Mean Density", "The average density of the entire segmented volume"),
    ("Standard Deviation of Density", "The standard deviation of density of the segmented volume"),
    ("Min Density", "The minimum density of the segmented volume"),
    ("Max Density", "The maximum density of the segmented volume"),
]


# Performs analysis on cortical bone
# image: 3D image black and white of bone
# mask: 3D labelmap of bone area, including cavities
# voxSize: The physical side length of the voxels, in mm 
# slope, intercept and scale: parameters of the equation for converting image values to mgHA/ccm
# output: The name of the output directory
def main(inputImg, inputMask, voxSize, slope, intercept, name, output):
    imgData = readImg(inputImg)
    (_, maskData) = readMask(inputMask)
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

    header = [field[0] for field in OUTPUT_FIELDS]

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
