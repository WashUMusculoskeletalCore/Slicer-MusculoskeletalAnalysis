# Slicer-MusculoskeletalAnalysis

Musculoskeletal Analysis extension for 3D Slicer.

<p align="center">
  <img width="50%" src="Scripted/MusculoskeletalAnalysis/Resources/Icons/MusculoskeletalAnalysis.png" alt="MusculoskeletalAnalysis Logo"/>
</p>

## How to use
1. Load a DICOM 3D image using the Add DICOM Data module.
2. Create a segment representing the area to analyze using the Segmentations and Segment Editor modules.
* **Cortical**: Segment should contain the bone including pores, but exclude the medullary cavity.
* **Cancellous**: Segement should contain cancellous bone and the spacing between bone, but exclude the surrounding cortical bone.
* **Density**: Segment should contain whatever area you want measured.
* **Intervertebral**: This function uses two segments, as thresholding alone may not be as effective at cleanly seperating NP from AF. One segment should contain the entire disc, the second should contrain just the Nucleus Pulposus. Order does not matter, as the analysys will identify which is which based on size.
3. Select which type of analysis you wish to perform.
4. Use the Threshold Selector to select the values for bone. Used to seperate bone from pores in cortical analysis and spacing in cancellous analysis. Skip this step for intervertebral disc analysis.
5. (Optional) Use the Advanced tab if the volume is not loaded from a DICOM.
6. Use the Output Directory Selector to select a directory. Output files will be created in this directory if they do not already exist, or will be appended to if they do.

## Musculoskeletal Analysis

### IO: Input/output parameters

* **Input Volume**: A 3d image of the bone.
* **Analysis Segment**: A segment of the image containing the bone area to analyse.
* **Threshold**: Threshold values representing bone.
* **Analysis**: Select the analysis to perform.
* **Output Directory**: The location to save the output file to.

### Advanced tab

The program requires information from certain DICOM tags to run. Normally it can retrieve that information from the volume node, but if the volume node does not have those tags(i.e, if you are using a copy of the original volume, or your data came from a different format), you can either select a node that does, or enter the values manually.

## Cortical Analysis

### IO: Input/output parameters

* **Input Volume**: A 3d image of the bone.
* **Bone Segment**: A segment of the image containing the cortical bone area. Includes pores, excludes the medullary cavity.
* **Threshold**: Threshold values representing bone. Used to seperate bone from pores.
* **Output Directory**: The location to save the output file to.

### Output File

The output file is a `tsv` file named `cortical.txt` with the following columns:

* **Date Analysis Performed**: The current date
* **Input Volume**: Name of the input volume
* **Mean Cortical Thickness (mm)**: The mean thickness of the bone, measured by largest sphere thickness, in milimeters
* **Cortical Thickness Standard Deviation (mm)**: The standard deviation of the above measurement
* **Tissue Mineral Density(mgHA/cm^3)**: The mean density of the bone, measured in miligrams of hydroxyapatite per cubic centimeter
* **Porosity**: The fraction of the bone area made up of pores
* **Total Area (mm^2)**: The area of the bone and medullary cavity. All areas are measured in average square milimeters per slice
* **Bone Area (mm^2)**: The area of the bone
* **Medullary Area (mm^2)**: The area of the medullary cavity
* **Polar Moment of Interia(mm^4)**: The moment of intertia around the z-axis, based on the shape of the mask. Measured in mm^4
* **Voxel Dimension (mm)**: The side length of one voxel, measured in milimeters

## Cancellous Analysis

### IO: Input/output parameters

* **Input Volume:** A 3d image of the bone.
* **Bone Segment:** A segment of the image containing the cancellous bone area. Includes the medullary cavity, excludes surrounding cotical bone.
* **Threshold:** Threshold values representing bone. Used to seperate bone from cavity.
* **Output Directory:** The location to save the output file to.


### Output File

The output file is a `tsv` file named `cancellous.txt` with the following columns:

* **Date Analysis Performed**: The current date
* **Input Volume**: Name of the input volume
* **Total Volume (mm^3)**: The volume of the segmented area
* **Bone Volume (mm^3)**: The volume of cancellous bone in the segmented area, calculated using marching cubes
* **Bone Volume/Total Volume**: The fraction of the volume that is bone
* **Mean Trabecular Thickness (mm)**: The mean thickess of the bone, measured using largest sphere thickness, in milimeters
* **Trabecular Thickness Standard Deviation (mm)**: The standard deviation of the mean trabecular thickness
* **Mean Trabecular Spacing (mm)**: The mean thickness of the non area not containing bone in milimeters, measured using the same method as bone thickness.
* **Trabecular Spacing Standard Deviation (mm)**: The standard deviation of the mean trabecular spacing
* **Trabecular Number**: Approximated as inverse of trabecular spacing
* **Structure Model Index**: A measurement of the trabecular shape. 0 is a plate, 3 is a rod, 4 is a sphere
* **Connectivity Density**: A measurement of the number of connections per volume, based on the Euler characteristic of the bone after removing isolated components and holes
* **Tissue Mineral Density(mgHA/cm^3)**: The mean density of the bone, measured in miligrams of hydroxyapatite per cubic centimeter
* **Voxel Dimension (mm)**: The side length of one voxel, measured in milimeters
* **Lower Threshold**: The lower threshold value for bone
* **Upper Threshold**: The upper threshold value for bone

## Density Analysis

### IO: Input/output parameters

* **Input Volume**: A 3d image of the bone.
* **Bone Segment**: A segmentation of the image containing the bone area to be measured.
* **Output Directory**: The location to save the output file to.

### Output File

The output file is a `tsv` file named `density.txt` with the following columns:.

* **Date Analysis Performed**: The current date
* **Input Volume**: Name of the input volume
* **Area by Slice**: The area of the segment in each slice of each slice
* **Mean Density by Slice**: The average density of the segmented area each slice
* **Standard Deviation of Density by Slice**: The standard deviation of the density of each slice
* **Min Density by Slice**: The lowest density in the segment of each slice
* **Max Density by Slice**: The highest density in the segment of each slice
* **Mean Area**: The mean area of the segment of all slices
* **Standard Deviation of Area**: The standard deviation of the segmented area of all slices
* **Min Area**: The area of the smallest segment slice
* **Max Area**: The area of the largest segment slice
* **Mean Density**: The average density of the entire segmented volume
* **Standard Deviation of Density**: The standard deviation of density of the segmented volume
* **Min Density**: The minimum density of the segmented volume
* **Max Density**: The maximum density of the segmented volume

## Intervertebral Analysis

### IO: Input/output parameters

* **Input Volume**: A 3d image of an intervertebral disc
* **Segement1** and **Segment2**: Two segmentations containing the disc and the nucleus pulposus. (Differentiated by size)
* **Output Directory**: The location to save the output file to.

### Output File

The output file is a `tsv` file named `intervertebral.txt` with the following columns:

* **Date Analysis Performed**: The current date
* **Input Volume**: Name of the input volume
* **Disc Volume (mm^3)**: The volume of the disc
* **Nucleus Pulposus Volume (mm^3)**: The volume of the NP
* **Volume Ratio**: The ratio of whole disc volume to NP volume
* **Annulus Fibrosus Width (mm)**: The width of the AF, calculated by using rotating calipers algorithm on each slice and finding the maximum width
* **Nucleus Pulposus Width (mm)**: The width of the NP, calculated using the same method as AF width
* **Disc Height (mm)**: The height of the disc at its center
* **Disc Height Ratio**: The ratio of disc height to disc width
* **Voxel Dimension (mm)**: The side length of one voxel, measured in milimeters

## Tutorials:

### Cortical Analysis:
1. Load Cortical1 and CorticalMask1 from the Sample Data Module.
2. Open the Musculoskeletal Analysis Module under Quantification.
3. Set Analysis to "Cortical Bone".
4. Set Input Volume to Cortical1.
5. Set Analysis Segment to CorticalMask1 and Segment_1.
6. Use the sliders to set Threshold to 4000-10000.
7. Open the Advanced tab and click "Enter DICOM tags manually".
8. Set values to 0.0073996, 4096, 365.712, -199.725998, and 0.4939.
9. Click the "..." next to Output Directory to open the directory selection menu, and select a location to save files to.
10. Click "Apply".

### Cancellous Analysis
1. Load Cancellous1 and CancellousMask1 from the Sample Data Module.
2. Open the Musculoskeletal Analysis Module under Quantification.
3. Set Analysis to "Cancellous Bone".
4. Set Input Volume to Cancellous1.
5. Set Analysis Segment to CancellousMask1 and Segment_1.
6. Use the sliders to set Threshold to 1500-10000.
7. Open the Advanced tab and click "Enter DICOM tags manually".
8. Set values to 0.0073996, 4096, 365.712, -199.725998, and 0.4939.
9. Click the "..." next to Output Directory to open the directory selection menu, and select a location to save files to.
10. Click "Apply".

### Density Analysis
1. Load Cancellous1 and CancellousMask1 from the Sample Data Module.
2. Open the Musculoskeletal Analysis Module under Quantification.
3. Set Analysis to "Bone Density".
4. Set Input Volume to Cancellous1.
5. Set Analysis Segment to CancellousMask1 and Segment_1.
6. Use the sliders to set Threshold to 1500-10000.
7. Open the Advanced tab and click "Enter DICOM tags manually".
8. Set values to 0.0073996, 4096, 365.712, -199.725998, and 0.4939.
9. Click the "..." next to Output Directory to open the directory selection menu, and select a location to save files to.
10. Click "Apply".

### Intervertebral Analysis
1. Load Intervertebral1 and IntervertebralMask1 from the Sample Data Module.
2. Open the Musculoskeletal Analysis Module under Quantification.
3. Set Analysis to "Intervertebral Disc".
4. Set Input Volume to Intervertebral1.
5. Set Analysis Segment to IntervertebralMask1 and check Segment_1 and Segment_2.
6. Open the Advanced tab and click "Enter DICOM tags manually".
7. Set "Voxel Size" to 0.01, leave the other fields blank.
8. Click the "..." next to Output Directory to open the directory selection menu, and select a location to save files to.
9. Click "Apply".

## Python Dependencies

The following additional python packages are required and will be installed the corresponding analysis functions are run:

|                | Cortical Analysis  | Cancellous Analysis | Density Analysis   | Intervertebral Analysis |
|----------------|--------------------|---------------------|--------------------|-------------------------|
| `pynrrd`       | :white_check_mark: | :white_check_mark:  | :white_check_mark: | :white_check_mark:      |
| `scikit-image` | :white_check_mark: | :white_check_mark:  |                    |                         |
| `scipy`        | :white_check_mark: | :white_check_mark:  |                    |                         |
| `trimesh`      |                    | :white_check_mark:  |                    |                         |

## Screenshots

| ![Musculoskeletal Analysis](Scripted/MusculoskeletalAnalysis/Resources/Icons/Screenshot.png) |
|--|
| <sub>_User interface of the Musculoskeletal Analysis module._</sub> |

## License

This software is licensed under the terms of the [MIT](LICENSE.txt).

