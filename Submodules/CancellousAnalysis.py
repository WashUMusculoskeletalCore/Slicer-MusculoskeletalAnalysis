#!/usr/bin/env python-real

import sys
import os
from datetime import date
import numpy as np
try:
    from skimage import measure
except:
    from slicer.util import pip_install
    pip_install("scikit-image")
    from skimage import measure
from tools.crop import crop
from tools.thickness import findSpheres
from tools.writeReport import writeReport
import tools.reader as reader
import tools.shape as shape
from DensityAnalysis import densityMap

# Performs analysis on cancellous bone
# image: 3D image black and white of bone
# mask: 3D labelmap of bone area, including cavities
# threshold: The threshold for bone in the image. Any pixels with a higher value will be considered bone.
# voxSize: The physical side length of the voxels, in mm 
# slope, intercept and scale: parameters for density conversion
# output: The name of the output directory
def main(inputImg, inputMask, lower, upper, voxSize, slope, intercept, output):
    imgData=reader.readImg(inputImg)
    (_, maskData) = reader.readMask(inputMask)
    
    (maskData, imgData) = crop(maskData, imgData)
    trabecular = (imgData > lower) & (imgData <= upper)
    boneMesh = shape.bWshape(trabecular)
    boneVolume=boneMesh.volume * voxSize**3
    totalVolume = np.count_nonzero(maskData) * voxSize**3
    bvtv = boneVolume/totalVolume
    print("""<filter-progress>{}</filter-progress>""".format(.20))
    sys.stdout.flush()
    background = np.bitwise_and(maskData, np.invert(trabecular))
    rads = findSpheres(trabecular)
    diams = rads * 2 * voxSize
    thickness = np.mean(diams)
    thicknessStd = np.std(diams)
    print("""<filter-progress>{}</filter-progress>""".format(.40))
    sys.stdout.flush()
    rads = findSpheres(background)
    diams = rads * 2 * voxSize
    spacing = np.mean(diams)
    spacingStd = np.std(diams)
    trabecularNum = 1/spacing
    print("""<filter-progress>{}</filter-progress>""".format(.60))
    sys.stdout.flush()
    # SMI
    bS = boneMesh.area*(voxSize**2)
    dr = 0.000001
    newVert=np.add(boneMesh.vertices, boneMesh.vertex_normals*dr)
    boneMesh=shape.updateVertices(boneMesh, newVert)
    dS = (boneMesh.area*(voxSize**2))-bS
    dr = dr*voxSize
    SMI=(6*boneVolume*(dS/dr)/(bS**2))
    print("""<filter-progress>{}</filter-progress>""".format(.80))
    sys.stdout.flush()
    # Calculate density
    density = densityMap(imgData, slope, intercept)
    tmd = np.mean(density[trabecular])

    # Connnectivity
    labelmap=measure.label(np.invert(trabecular), connectivity=1)
    largest=np.argmax(np.bincount(labelmap[np.nonzero(labelmap)]))
    trabecular=labelmap!=largest

    labelmap=measure.label(trabecular, connectivity=3)
    largest=np.argmax(np.bincount(labelmap[np.nonzero(labelmap)]))
    trabecular=labelmap==largest

    phi = measure.euler_number(trabecular, connectivity=3)

    connD = (1-phi)/totalVolume

    


    fPath = os.path.join(output, "cancellous.txt")

    header = [
        'Date Analysis Performed',
        'File ID',
        'Total Volume (mm^3)',
        'Bone Volume (mm^3)',
        'Bone Volume/Total Volume',
        'Mean Trabecular Thickness (mm)',
        'Trabecular Thickness Standard Deviation (mm)',
        'Mean Trabecular Spacing (mm)',
        'Trabecular Spacing Standard Deviation (mm)',
        'Trabecular Number',
        'Structure Model Index',
        'Connectivity Density',
        'Tissue Mineral Density(mgHA/cm^3)',
        'Voxel Dimension (mm)',
        'Lower Threshold',
        'Upper Threshold'
    ]
    data = [
        date.today(),
        fPath,
        totalVolume,
        boneVolume,
        bvtv,
        thickness,
        thicknessStd,
        spacing,
        spacingStd,
        trabecularNum,
        SMI,
        connD,
        tmd,
        voxSize,
        lower,
        upper
    ]

    writeReport(fPath, header, data)

if __name__ == "__main__":
    if len(sys.argv) < 9:
        print(sys.argv)
        print(len(sys.argv))
        print("Usage: CancellousAnalysis <input> <mask> <lowerThreshold> <upperThreshold> <voxelSize> <slope> <intercept> <output>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7]), str(sys.argv[8]))
