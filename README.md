# Slicer-MusculoskeletalAnalysis
Musculoskeletal Analysis extension for 3D Slicer. Currently Alpha

![Alt text](/Scripted/MusculoskeletalAnalysis/Resources/Icons/Screenshot.png?raw=true)

## Dependencies
The following additional python packages are required:<br/>
pynrrd: All analysis<br/>
scikit-image: Cortical Analysis and Cancellous Analysis<br/>
scipy: Cortical Analysis and Cancellous Analysis<br/>
trimesh: Cancellous Analysis

Packages will be installed when the associated analysis functions are run.


## How to use
1. Load a DICOM 3D image using the Add DICOM Data module.
2. Create a segment representing the area to analyze using the Segmentations and Segment Editor modules. See the input parameters of the function for more details on what to include in the segment.
3. Select which type of analysis you wish to perform.
4. Use the Threshold Selector to select the values for bone. Used to seperate bone from pores in cortical analysis and spacing in cancellous analysis.
5. (Optional) Use the Advanced tab if the volume is not loaded from a DICOM.
6. Use the Output Directory Selector to select a directory. Output files will be created in this directory if they do not already exist, or will be appended to if they do.

## Advanced tab
The program requires information from certain DICOM tags to run. Normally it can retrieve that information from the volume node, but if the volume node does not have those tags(i.e, if you are using a copy of the original volume, or your data came from a different format), you can either select a node that does, or enter the values manually.


## Cortical Analysis
### Input Parameters:
Input Volume: A 3d image of the bone.
Bone Segment: A segment of the image containing the cortical bone area. Includes pores, excludes the medullary cavity.
Threshold: Threshold values representing bone. Used to seperate bone from pores.
Output Directory: The location to save the output file to. File will be a tsv file named cortical.txt. 

### Output Parameters:
Date Analysis Performed: The current date
File ID: The output filepath
Mean Cortical Thickness: The mean thickness of the bone, measured by largest sphere thickness, in milimeters.
Cortical Thickness Standard Deviation: The standard deviation of the above measurement.
Tissue Mineral Density: The mean density of the bone, measured in miligrams of hydroxyapatite per cubic centimeter
Porosity: The fraction of the bone area made up of pores
Total Area: The area of the bone and medullary cavity. All areas are measured in average square milimeters per slice
Bone Area: The area of the bone
Medullary Area: The area of the medullary cavity
Polar Moment of Interia: The moment of intertia around the z-axis, based on the shape of the mask. Measured in mm^4
Voxel Dimension: The side length of one voxel, measured in milimeters


## Cancellous Analysis
### Input Parameters:
Input Volume: A 3d image of the bone.
Bone Segment: A segment of the image containing the cancellous bone area. Includes the medullary cavity, excludes surrounding cotical bone.
Threshold: Threshold values representing bone. Used to seperate bone from cavity.
Output Directory: The location to save the output file to. File will be a tsv file named cancellous.txt.


### Output Parameters:
Date Analysis Performed: The current date
File ID: The output filepath
Total Volume: The volume of the segmented area
Bone Volume: The volume of cancellous bone in the segmented area, calculated using marching cubes
Bone Volume/Total Volume: The fraction of the volume that is bone
Mean Trabecular Thickness: The mean thickess of the bone, measured using largest sphere thickness, in milimeters
Trabecular Thickness Standard Deviation: The standard deviation of the above mean
Mean Trabecular Spacing: The mean thickness of the non area not containing bone in milimeters, measured using the same method as bone thickness.
Trabecular Spacing Standard Deviation: The standard deviation of the above mean
Trabecular Number: Approximated as inverse of trabecular spacing
Structural Model Index: A measurement of the trabecular shape. 0 is a plate, 3 is a rod, 4 is a sphere
Connectivity Density: A measurement of the number of connections per volume, based on the Euler characteristic of the bone after removing isolated components and holes
Tissue Mineral Density: The mean density of the bone, measured in miligrams of hydroxyapatite per cubic centimeter
Voxel Dimension: The side length of one voxel, measured in milimeters
Lower Threshold: The lower threshold value for bone
Upper Threshold: The upper threshold value for bone

## Density Analysis
### Input Parameters:
Input Volume: A 3d image of the bone.
Bone Segment: A segmentation of the image containing the bone area to be measured.
Output Directory: The location to save the output file to. File will be a tsv file named density.txt.

### Output Parameters:
Date Analysis Performed: The current date
File ID: The output filepath
Area by Slice: The area of the segment in each slice of each slice
Mean Density by Slice: The average density of the segmented area each slice
Standard Deviation of Density by Slice: The standard deviation of the density of each slice
Min Density by Slice: The lowest density in the segment of each slice
Max Density by Slice: The highest density in the segment of each slice
Mean Area: The mean area of the segment of all slices
Standard Deviation of Area: The standard deviation of the segmented area of all slices
Min Area: The area of the smallest segment slice
Max Area: The area of the largest segment slice
Mean Density: The average density of the entire segmented volume
Standard Deviation of Density: The standard deviation of density of the segmented volume
Min Density: The minimum density of the segmented volume
Max Density: The maximum density of the segmented volume

