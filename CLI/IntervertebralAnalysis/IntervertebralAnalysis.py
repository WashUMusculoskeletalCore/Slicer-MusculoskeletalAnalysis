#!/usr/bin/env python-real

import sys
import os
from datetime import date

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MusculoskeletalAnalysisCLITools import (
   crop,
   readImg,
   readMask,
   width,
   writeReport,
)


OUTPUT_FIELDS = [
    ("Date Analysis Performed", "The current date"),
    ("Input Volume", "Name of the input volume"),
    ("Disc Volume (mm^3)", "The volume of the disc"),
    ("Nucleus Pulposus Volume (mm^3)", "The volume of the NP"),
    ("Volume Ratio", "The ratio of whole disc volume to NP volume"),
    ("Annulus Fibrosus Width (mm)", "The width of the AF, calculated by using rotating calipers algorithm on each slice and finding the maximum width"),
    ("Nucleus Pulposus Width (mm)", "The width of the NP, calculated using the same method as AF width"),
    ("Disc Height (mm)", "The height of the disc at its center"),
    ("Disc Height Ratio", "The ratio of disc height to disc width"),
    ("Voxel Dimension (mm)", "The side length of one voxel, measured in milimeters"),
]


def main(inputImg, inputMask1, inputMask2, voxSize, name, output):
    imgData = readImg(inputImg)
    (_, maskData1) = readMask(inputMask1)
    (_, maskData2) = readMask(inputMask2)
    # Set the np mask to the smaller one
    if np.count_nonzero(maskData1) > np.count_nonzero(maskData2):
        (maskData, npData, imgData) = crop(maskData1, maskData2, imgData)
    else:
        (maskData, npData, imgData) = crop(maskData2, maskData1, imgData)
    (maskData, npData, imgData) = crop(maskData, npData, imgData)
    if np.count_nonzero(maskData) == 0 or np.count_nonzero(npData) == 0:
         raise Exception("Segmentation mask is empty.")

    volume = np.count_nonzero(maskData) * voxSize**3
    npVolume = np.count_nonzero(npData) * voxSize**3
    vr = npVolume/volume

    print("""<filter-progress>{}</filter-progress>""".format(.33))
    sys.stdout.flush()

    afWidth= width(maskData) * voxSize
    npWidth = width(npData) * voxSize

    # Find the center
    xcent = int(np.rint(np.mean(np.nonzero(maskData)[0])))
    ycent = int(np.rint(np.mean(np.nonzero(maskData[1]))))
    center = np.nonzero(maskData[xcent,ycent,:])
    height = (np.max(center)-np.min(center)) * voxSize

    hw = height/afWidth

    print("""<filter-progress>{}</filter-progress>""".format(.66))
    sys.stdout.flush()

    fPath = os.path.join(output, "intervertebral.txt")
    header = [field[0] for field in OUTPUT_FIELDS]
    data = [
        date.today(),
        name,
        volume,
        npVolume,
        vr,
        afWidth,
        npWidth,
        height,
        hw,
        voxSize
    ]

    writeReport(fPath, header, data)



if __name__ == "__main__":
    if len(sys.argv) < 7:
        print(sys.argv)
        print("Usage: Intervertebral Analysis <input> <mask1> <mask2> <voxelSize> <name> <output>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), str(sys.argv[5]), str(sys.argv[6]))

