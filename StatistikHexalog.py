import sys, os

'''
    importHexalogFiles
    path String: path to Hexalog File
    lst_hexalog List: list of Hexalog Events Roll, Pitch, Yaw

    return lst_hexalog: (Roll, Pitch, Yaw)*
'''

def importHexalogFiles(path):
    lst_hexalog = list()
    hexalogfile = open(path, "rt")

    previous_imu = ()
    value_cam = ()

    for row in list(hexalogfile)[1:]:
        row = row.replace("\n", "")
        values = row.split(", ")

        if values[0] == "IMU":
            if value_cam == ():
                previous_imu = values
            else:
                lst_hexalog.append((previous_imu, value_cam, values))
                previous_imu = values
                value_cam = ()

        elif values[0] == "CAM":
            value_cam = values

    return lst_hexalog

def analyzeHexalogEvents(file_name, values):
    def delta(first_value, second_value):
        diff = first_value - second_value
        if diff > 0:
            return diff
        elif diff < 0:
            return -diff
        else:
            return 0

    max_delta_gyroX = 0
    max_delta_gyroY = 0
    max_delta_gyroZ = 0

    min_delta_gyroX = 0
    min_delta_gyroY = 0
    min_delta_gyroZ = 0

    max_gyroX = 0
    max_gyroY = 0
    max_gyroZ = 0

    for value in values:
        previous_imu = value[0]
        next_imu = value[2]

        dX = delta(float(previous_imu[2]), float(next_imu[2]))
        if max_delta_gyroX < dX: max_delta_gyroX = dX
        if min_delta_gyroX > dX: min_delta_gyroX = dX
        if max_gyroX < float(previous_imu[2]): max_gyroX = float(previous_imu[2])
        if max_gyroX < float(next_imu[2]): max_gyroX = float(next_imu[2])

        dY = delta(float(previous_imu[3]), float(next_imu[3]))
        if max_delta_gyroY < dY: max_delta_gyroY = dY
        if min_delta_gyroY > dY: min_delta_gyroY = dY
        if max_gyroY < float(previous_imu[3]): max_gyroY = float(previous_imu[3])
        if max_gyroY < float(next_imu[3]): max_gyroY = float(next_imu[3])

        dZ = delta(float(previous_imu[4]), float(next_imu[4]))
        if max_delta_gyroZ < dZ: max_delta_gyroZ = dZ
        if min_delta_gyroZ > dZ: min_delta_gyroZ = dZ
        if max_gyroZ < float(previous_imu[4]): max_gyroZ = float(previous_imu[4])
        if max_gyroZ < float(next_imu[4]): max_gyroZ = float(next_imu[4])

    print("Statistic of " + file_name)
    print("Maximum (x, y, z): " + str(max_gyroX) + ", " + str(max_gyroY) + ", " + str(max_gyroZ))
    print("Maximum Delta (x, y, z): " + str(max_delta_gyroX) + ", " + str(max_delta_gyroY) + ", " + str(max_delta_gyroZ))
    print("Minimum Delta (x, y, z): " + str(min_delta_gyroX) + ", " + str(min_delta_gyroY) + ", " + str(min_delta_gyroZ))

file_pictureCentres = r"E:\Blindert\HexaLogs\2020-09-21 10-42-48.log" #sys.argv[1]
file_name, file_extension = os.path.splitext(file_pictureCentres)

values_hexalog = importHexalogFiles(file_pictureCentres)
analyzeHexalogEvents(file_pictureCentres, values_hexalog)