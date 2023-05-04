import SimpleITK as sitk
from nrrd import read

# Reads an image file as input, returns the image as a numpy array     
def readImg(inputImg):   
    imgReader = sitk.ImageFileReader()
    imgReader.SetFileName(inputImg)
    image = imgReader.Execute()
    image = sitk.DICOMOrient(image, 'SPL')
    imgData = sitk.GetArrayFromImage(image)
    return imgData

# Reads an nrrd file as input, returns the image as a binary numpy array
def readMask(inputMask):
    maskReader = read(inputMask)
    maskHeader = maskReader[1:]
    maskData = maskReader[0].astype('bool')
    return maskHeader, maskData
