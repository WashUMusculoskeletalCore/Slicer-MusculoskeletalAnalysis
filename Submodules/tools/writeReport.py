import os.path
import numpy as np

# Writes data to a tab seperated format
# filepath: The filename and path of the file to write to
# header: A list of collumn names, written as the first line if this is a new file
# data: A list of data elements, each element can be single or a numpy ndarray
def writeReport(filepath, header, data):
    if os.path.exists(filepath):
        # If the file exist open and append to it
        fOut = open(filepath, "a")
    else:
        # If the file does not exist create it and write header
        fOut = open(filepath, "w")
        if len(header) > 0:
            for h in header[:-1]:
                fOut.write(h+"\t")
            fOut.write(header[-1]+"\n")
    if len(data) > 0:
        # Write the data
        # If data contains ndarray write multiple lines, skipping over collumns that are not ndarray
        maxLength = max(numEl(d) for d in data)
        for i in range(maxLength):
            for j in range(len(data)):
                d = data[j]
                if numEl(d) > i:
                    if isinstance(d, np.ndarray):
                        fOut.write(str(d[i]))
                    else:
                        fOut.write(str(d))
                if j < len(data)-1:
                    fOut.write("\t")
                else:
                    fOut.write("\n")
    fOut.close()

# Gets the number of elements in a datapoint,
# Returns the length of ndarray or 1
def numEl(d):
    if isinstance(d, np.ndarray):
        return len(d)
    else:
        return 1