"""Converts slicer image and segmentation volumes into numpy format."""


def readImg(inputImg):   
    """Reads an image file as input, returns the image as a numpy array."""
    import SimpleITK as sitk

    imgReader = sitk.ImageFileReader()
    imgReader.SetFileName(inputImg)
    image = imgReader.Execute()
    image = sitk.DICOMOrient(image, 'SPL')
    imgData = sitk.GetArrayFromImage(image)
    return imgData


def readMask(inputMask):
    """Reads an nrrd file as input, returns the image as a binary numpy array."""
    from nrrd import read

    maskReader = read(inputMask)
    maskHeader = maskReader[1:]
    maskData = maskReader[0].astype('bool')
    return maskHeader, maskData
