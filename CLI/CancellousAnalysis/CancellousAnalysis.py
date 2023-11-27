#!/usr/bin/env python-real

import sys
import os
from datetime import date

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MusculoskeletalAnalysisCLITools import (
  crop,
  bWshape,
  densityMap,
  findSpheres,
  readImg,
  readMask,
  updateVertices,
  writeReport,
)


OUTPUT_FIELDS = [
    ("Date Analysis Performed", "The current date"),
    ("Input Volume", "Name of the input volume"),
    ("Total Volume (mm^3)", "The volume of the segmented area"),
    ("Bone Volume (mm^3)", "The volume of cancellous bone in the segmented area, calculated using marching cubes"),
    ("Bone Volume/Total Volume", "The fraction of the volume that is bone"),
    ("Mean Trabecular Thickness (mm)", "The mean thickess of the bone, measured using largest sphere thickness, in milimeters"),
    ("Trabecular Thickness Standard Deviation (mm)", "The standard deviation of the mean trabecular thickness"),
    ("Mean Trabecular Spacing (mm)", "The mean thickness of the non area not containing bone in milimeters, measured using the same method as bone thickness."),
    ("Trabecular Spacing Standard Deviation (mm)", "The standard deviation of the mean trabecular spacing"),
    ("Trabecular Number", "Approximated as inverse of trabecular spacing"),
    ("Structure Model Index", "A measurement of the trabecular shape. 0 is a plate, 3 is a rod, 4 is a sphere"),
    ("Connectivity Density", "A measurement of the number of connections per volume, based on the Euler characteristic of the bone after removing isolated components and holes"),
    ("Tissue Mineral Density(mgHA/cm^3)", "The mean density of the bone, measured in miligrams of hydroxyapatite per cubic centimeter"),
    ("Voxel Dimension (mm)", "The side length of one voxel, measured in milimeters"),
    ("Lower Threshold", "The lower threshold value for bone"),
    ("Upper Threshold", "The upper threshold value for bone"),
]


# Performs analysis on cancellous bone
# image: 3D image black and white of bone
# mask: 3D labelmap of bone area, including cavities
# threshold: The threshold for bone in the image. Any pixels with a higher value will be considered bone.
# voxSize: The physical side length of the voxels, in mm
# slope, intercept and scale: parameters for density conversion
# output: The name of the output directory
def main(inputImg, inputMask, lower, upper, voxSize, slope, intercept, name, output):
    from skimage import measure

    imgData = readImg(inputImg)
    (_, maskData) = readMask(inputMask)
    
    (maskData, imgData) = crop(maskData, imgData)
    if np.count_nonzero(maskData) == 0:
         raise Exception("Segmentation mask is empty.")
    trabecular = (imgData > lower) & (imgData <= upper)
    # Create mesh using marching squares and calculate its volume
    boneMesh = bWshape(trabecular)
    boneVolume=boneMesh.volume * voxSize**3
    # Find volume of entire mask by counting voxels
    totalVolume = np.count_nonzero(maskData) * voxSize**3
    bvtv = boneVolume/totalVolume
    print("""<filter-progress>{}</filter-progress>""".format(.20))
    sys.stdout.flush()
    background = np.bitwise_and(maskData, np.invert(trabecular))
    # Get the thickness map and calculate the thickness
    rads = findSpheres(trabecular)
    diams = rads * 2 * voxSize
    thickness = np.mean(diams)
    thicknessStd = np.std(diams)
    print("""<filter-progress>{}</filter-progress>""".format(.40))
    sys.stdout.flush()
    # Get the thickness map for the background
    rads = findSpheres(background)
    diams = rads * 2 * voxSize
    spacing = np.mean(diams)
    spacingStd = np.std(diams)
    trabecularNum = 1/spacing
    print("""<filter-progress>{}</filter-progress>""".format(.60))
    sys.stdout.flush()
    # SMI
    # Calculated by finding a 3d mesh, expanding the vertices by a small amount, and calculate a value based on the relative difference in surface area
    # Measures the characteristics of the shape; 0 for plate-like, 3 for rod-like, 4 for sphere-like
    # Surface area
    bS = boneMesh.area*(voxSize**2)
    # Arbitrary small value. Reducing size increases accuracy, but risks being rounded to zero
    dr = 0.000001
    # Creates a new mesh by moving each vertex a small distance in the direction of its vertex normal, then find the difference in surface area
    newVert=np.add(boneMesh.vertices, boneMesh.vertex_normals*dr)
    boneMesh = updateVertices(boneMesh, newVert)
    dS = (boneMesh.area*(voxSize**2))-bS
    # Convert to mm
    dr = dr*voxSize
    # Apply the SMI formula
    SMI=(6*boneVolume*(dS/dr)/(bS**2))
    print("""<filter-progress>{}</filter-progress>""".format(.80))
    sys.stdout.flush()
    # Calculate density
    density = densityMap(imgData, slope, intercept)
    tmd = np.mean(density[trabecular])

    # Connnectivity
    # Remove disconected holes and islands
    labelmap=measure.label(np.invert(trabecular), connectivity=1)
    largest=np.argmax(np.bincount(labelmap[np.nonzero(labelmap)]))
    trabecular=labelmap!=largest
    # Holes use face connectivity, switch to vertex connectivity for islands
    labelmap=measure.label(trabecular, connectivity=3)
    largest=np.argmax(np.bincount(labelmap[np.nonzero(labelmap)]))
    trabecular=labelmap==largest

    # Find the euler characteristic
    # roughly equal to 2-2*number of holes
    phi = measure.euler_number(trabecular, connectivity=3)
    # connD gives an approximate measure of holes/connections per volume
    connD = (1-phi)/totalVolume




    fPath = os.path.join(output, "cancellous.txt")

    header = [field[0] for field in OUTPUT_FIELDS]

    data = [
        date.today(),
        name,
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
    if len(sys.argv) < 10:
        print(sys.argv)
        print(len(sys.argv))
        print("Usage: CancellousAnalysis <input> <mask> <lowerThreshold> <upperThreshold> <voxelSize> <slope> <intercept> <name> <output>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7]), str(sys.argv[8]), str(sys.argv[9]))
