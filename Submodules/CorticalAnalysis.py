#!/usr/bin/env python-real

import sys
import os
import numpy as np
from datetime import date
from tools.crop import crop
from tools.thickness import findSpheres
from tools.fill import fill
from tools.writeReport import writeReport
from tools.largestCC import largestCC
import tools.reader as reader
from DensityAnalysis import densityMap

# Performs analysis on cortical bone
# image: 3D image black and white of bone
# mask: 3D labelmap of bone area, including cavities
# lower, upper: The thresholds for bone in the image. Any pixels with a value in the range will be considered bone.
# voxSize: The physical side length of the voxels, in mm 
# slope, intercept and scale: parameters for density conversion
# output: The name of the output directory
def main(inputImg, inputMask, lower, upper, voxSize, slope, intercept, name, output):   
    imgData=reader.readImg(inputImg)
    (_, maskData) = reader.readMask(inputMask)
    (maskData, imgData) = crop(maskData, imgData)
    if np.count_nonzero(maskData) == 0:
         raise Exception("Segmentation mask is empty.")
    depth = np.shape(maskData)[2] * voxSize
    boneVolume = np.count_nonzero(maskData) * voxSize**3
    # Fill in hole to find medullary cavity
    filledMask = np.zeros_like(maskData)
    print("""<filter-progress>{}</filter-progress>""".format(.20))
    sys.stdout.flush()
    for sliceNum in range(maskData.shape[2]):
        filledMask[:,:,sliceNum] = fill(maskData[:,:,sliceNum], 5)
    # Calculate volumes and average area
    totalVolume = np.count_nonzero(filledMask) * voxSize**3
    medullarVolume = totalVolume-boneVolume
    boneArea = boneVolume/depth
    totalArea = totalVolume/depth
    medullarArea = medullarVolume/depth
    print("""<filter-progress>{}</filter-progress>""".format(.40))
    sys.stdout.flush()
    # PMOI
    # For each slice, calculate the second moment of area around the x-axis and y-axis
    # I = area*(distance from center)^2
    # PMOI = average of Ix+Iy
    ix = np.zeros(maskData.shape[2])
    iy = np.zeros(maskData.shape[2])
    # Calculate Ix and Iy for each slice
    for sliceNum in range(maskData.shape[2]):
        # Find the x center
        xDist = np.nonzero(maskData[:,:,sliceNum])[0]
        xCenter = np.mean(xDist)
        # Find distance from center squared times area. Convert from voxel units^4 to mm^4
        ix[sliceNum] = sum((xDist-xCenter)**2)*voxSize**4
        # Repeat for y
        yDist = np.nonzero(maskData[:,:,sliceNum])[1]
        yCenter = np.mean(yDist)
        iy[sliceNum] = sum((yDist-yCenter)**2)*voxSize**4
    # Find the average of the sum
    pMOI = np.mean(ix)+np.mean(iy)
    # Porosity
    # Finds the percentage of the mask that is not in the threshold
    porousBone = (imgData > lower) & (imgData <= upper) & maskData
    porosity = 1 - (np.count_nonzero(porousBone)/np.count_nonzero(maskData))
    print("""<filter-progress>{}</filter-progress>""".format(.60))
    sys.stdout.flush()
    # Thickness
    # Remove disconnected areas
    rads = largestCC(maskData)
    # Convert to thickness map
    rads = findSpheres(rads)
    # Find nonzero values, double to convert to diameters, and find average
    rads = rads[np.nonzero(rads)]
    diams = rads * 2 * voxSize
    thickness = np.mean(diams)
    thicknessStd = np.std(diams)
    print("""<filter-progress>{}</filter-progress>""".format(.80))
    sys.stdout.flush()
    # Calculate Density
    # Density calculations are based on DICOM metadata
    density = densityMap(imgData, slope, intercept)
    tmd = np.mean(density[maskData])
    
    fPath = os.path.join(output, "cortical.txt")

    header = [
        'Date Analysis Performed',
        'Input Volume',
        'Mean Cortical Thickness (mm)',
        'Cortical Thickness Standard Deviation (mm)',
        'Tissue Mineral Density(mgHA/cm^3)',
        'Porosity',
        'Total Area (mm^2)',
        'Bone Area (mm^2)',
        'Medullary Area (mm^2)',
        'Polar Moment of Interia(mm^4)',
        'Voxel Dimension (mm)'
    ]
    data = [
        date.today(),
        name,
        thickness,
        thicknessStd,
        tmd,
        porosity,
        totalArea,
        boneArea,
        medullarArea,
        pMOI,
        voxSize
    ]

    writeReport(fPath, header, data)



if __name__ == "__main__":
    if len(sys.argv) < 10:
        print(sys.argv)
        print("Usage: CorticalAnalysis <input> <mask> <lowerThreshold> <upperThreshold> <voxelSize> <slope> <intercept> <name> <output>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7]), str(sys.argv[8]), str(sys.argv[9]))

