import re

def fix_labels(header):

    for i, label in enumerate(header):
        if re.search("Unix", label):
            header[i] = "Timestamp"
        if (re.search("Accel", label) and re.search("X", label)):
            header[i] = "Accel_X"
        if (re.search("Accel", label) and re.search("Y", label)):
            header[i] = "Accel_Y"
        if (re.search("Accel", label) and re.search("Z", label)):
            header[i] = "Accel_Z"
        if (re.search("Gyro", label) and re.search("X", label)):
            header[i] = "Gyro_X"
        if (re.search("Gyro", label) and re.search("Y", label)):
            header[i] = "Gyro_Y"
        if (re.search("Gyro", label) and re.search("Z", label)):
            header[i] = "Gyro_Z"
        if re.search("Pressure", label):
            header[i] = "Pressure"
        if re.search("Temp", label):
            header[i] = "Temperature"
        if re.search("GSR", label):
            header[i] = "GSR"

    return header