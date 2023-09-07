# Converts an image to a density map the same shape and size
# Uses parameters from DICOM metadata to find linear relationship between pixel value and physical density
def densityMap(img, slope, intercept):
    return img * slope + intercept