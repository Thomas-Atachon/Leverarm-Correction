import os, sys, math

def importCamFiles(path, offsetZ):
    '''
        importCamFiles Function
        :param path String: path to CAM File
        :param lst_cam List: list of GNSS antenna positions

        :return lst_cam: (latitude, longitude, height)*
    '''

    lst_cam = list()
    camfile = open(path, "rt")
    for row in camfile:
        row = row.replace("\n", "")
        values = row.split(",")
        latitude = values[8]
        longitude = values[9]
        height = str(float(values[10]) + offsetZ)
        lst_cam.append((latitude, longitude, height))

    return lst_cam

def importJustinFiles(path, offsetZ):
    '''
        importJustinFiles Function
        :param path String: path to Justin File
        :param lst_justin List: List of RTK GNSS antenna positions

        :return lst_justin: (northing, easting, height)*
    '''

    lst_justin = list()
    justinfile = open(path, "rt")
    marker = 0
    for row in justinfile:
        row = row.replace("\x00", "").replace(" \n", "")
        if marker < 2:
            if row[0:7] == "Event |":
                marker += 1
            elif row[0:6] == "------":
                marker += 1
        else:
            values = row.split(" | ")
            if len(values) >= 7:
                north = values[2].replace(",", ".")
                east = values[3].replace(",", ".")
                height = str(float(values[4].replace(",", ".")) + offsetZ)
                accuracy = values[5].replace(",", ".")
                lst_justin.append((north, east, height, accuracy))
                
    return lst_justin

def importPictureNames(path):
    '''
        importPictureNames Function
        :param path String: path to pictures directory
        :param lst_picturenames List: list of picturesnames

        :return lst_picturenames: picturename*
    '''

    lst_picturenames = list()
    directory = os.listdir(path)
    for file in directory:
        if os.path.isfile(os.path.join(path, file)):
            lst_picturenames.append(file)

    return lst_picturenames

def importHexalogFiles(path):
    '''
        importHexalogFiles Function
        :param path String: path to Hexalog File
        :param lst_hexalog List: list of Hexalog Events Roll, Pitch, Yaw

        :return lst_hexalog: (Roll, Pitch, Yaw)*
    '''

    lst_hexalogs = list()
    hexalogfile = open(path, "rt")
    for row in list(hexalogfile)[1:]:
        row = row.replace("\n", "")
        values = row.split(", ")
        if values[0] == "CAM":
            lst_hexalogs.append((values[9], values[10], values[11]))

    return lst_hexalogs

def matchPicturWithEvents(lst_event, lst_picturenames, skipPictures = 0, skipEvents = 0):
    '''
        matchPicturWithEvents Function
        :param lst_event List: list of events from function importCamFiles or importJustinFiles
        :param lst_picturenames list: list of picturesnames
        :param skipPictures integer: count of skipping pictures
        :param skipEvents integer: count of skipping events

        :return lst_matched: (picturename, event)*
    '''

    lst_matched = list()

    lst_event = lst_event[skipEvents:]
    lst_picturenames = sorted(lst_picturenames)[skipPictures:]

    print("Number of Events/Pictures: " + str(len(lst_event)) + "/" + str(len(lst_picturenames)))
    if len(lst_event) == len(lst_picturenames):
        for i in range(len(lst_event)):
            lst_matched.append([lst_picturenames[i], lst_event[i][0:3], (), lst_event[i][3]])
    else:
        raise IndexError("number of pictures and events does not match")

    return lst_matched


def matchWithHexalogs(lst_matched, lst_hexalogs, skipHexalogs = 0):
    '''
        matchWithHexalogs Function
        :param lst_matched List:
        :param lst_hexalogs List: Hexalog Events Roll, Pitch, Yaw
        :param skipHexalogs Integer: events to skip

        :return lst_matched: (picturename, event, hexalogevent)*
    '''

    lst_hexalogs = lst_hexalogs[skipHexalogs:]

    print("Number of Hexalogevents/Pictures: " + str(len(lst_hexalogs)) + "/" + str(len(lst_matched)))
    if len(lst_matched) == len(lst_hexalogs):
        for i in range(len(lst_matched)):
            lst_matched[i][2] = lst_hexalogs[i]
    else:
        raise IndexError("number of pictures and hexalogs does not match")

    return lst_matched

def leverArmCorrection(orientation, leverarm):
    '''
        leverArmCorrection Function
        :param orientation Tuple: Roll, Pitch, Yaw
        :param leverarm: definiton of local translation

        :return dx, dy, dz: translation in global system in meters
    '''

    #pitch +/- 180 Grad nicht abgefangen, jedoch nicht notwendig
    roll, pitch, yaw = float(orientation[0])/180*math.pi, float(orientation[1])/180*math.pi, -float(orientation[2])/180*math.pi

    #Translation
    x0, y0, z0 = float(leverarm[1]), float(leverarm[0]), float(leverarm[2])

    #Rotation
    dx = x0*(math.cos(roll)*math.cos(yaw)) + \
        y0*(math.sin(roll)*math.sin(pitch)*math.cos(yaw) - math.cos(pitch)*math.sin(yaw)) + \
        z0*(math.sin(pitch)*math.sin(yaw) + math.sin(roll)*math.cos(pitch)*math.cos(yaw))
    dy = x0*(math.cos(roll)*math.sin(yaw)) + \
        y0*(math.cos(pitch)*math.cos(yaw) + math.sin(roll)*math.sin(pitch)*math.sin(yaw)) + \
        z0*(math.sin(roll)*math.cos(pitch)*math.sin(yaw) - math.sin(pitch)*math.cos(yaw))
    dz = -x0*(math.sin(roll)) + \
        y0*(math.cos(roll)*math.sin(pitch)) + \
        z0*(math.cos(roll)*math.cos(pitch))

    return dx, dy, dz

def matchLeverArmWithJustin(lst_matched, leverarm):
    '''
        matchLeverArmWithJustin Function
        :param lst_matched List:

        :return lst_matched:
    '''
    for row in lst_matched:
        dx, dy, dz = leverArmCorrection(row[2], leverarm)

        # Translation to global system
        y = float(row[1][0]) + dy
        x = float(row[1][1]) + dx
        z = float(row[1][2]) + dz

        row[1] = (str(y), str(x), str(z))

    return lst_matched

def matchLeverArmWithCam(lst_matched, leverarm):
    '''
        matchLeverArmWithCam Function
        :param lst_matched List:

        :return lst_matched:
    '''
    for row in lst_matched:
        dx, dy, dz = leverArmCorrection(row[2], leverarm)

        #WGS84 Radius of the large half-axis
        radius = 6378137

        center = row[1]
        latitude, longitude, height = float(center[0]), float(center[1]), float(center[2])
        extentOfLatitude = 2*math.pi*math.cos(latitude)*radius
        extentOfLongitude = 2*math.pi*radius

        # Translation to global system
        y = latitude + dy/extentOfLongitude*360
        x = longitude + dx/extentOfLatitude*360
        z = height + dz

        row[1] = (str(y), str(x), str(z))

    return lst_matched

def matchWithAccuracy(lst_matched, accuracy):
    '''
        matchWithAccuracy Function
        :param lst_matched List:
        :param accuracy float: Accuracy of the events

        :return lst_matched: (event, accuracy)*
    '''

    for row in lst_matched:
        row[3] = str(accuracy)
    return lst_matched

def exportMatched(lst_matched, export_file):
    '''
        exportMatched Function
        :param lst_matched List:
        :param export_file String: output file

        :return path: path of the export file
    '''

    export = open(export_file, "wt")

    for row in lst_matched:
        picturename = row[0]
        export.write(picturename)
        center = geodround(row[1][0], 4) + "," + geodround(row[1][1], 4) + "," + geodround(row[1][2], 4)
        export.write("," + center)
        accuracy = row[3]
        if accuracy is not None:
            export.write("," + accuracy)
        export.write("\n")
    print("exported to " + export_file)

    return export_file

def geodround(value, decimal):
    '''
    round Function
    :param value Float: value
    :param decimal Integer: decimal

    :return rounded: rounded value
    '''
    rounded_value = round(float(value), decimal)

    return str(rounded_value)

########################################################################################################################

''' Evaluate Parameters '''
parameters = {"pic": None, "cam": None, "justin": None, "hex": None,
              "ske": 0, "skp": 0, "skh": 0, "acc": None,
              "o": None,
              "lx": 0, "ly": 0, "lz": 0,
              "offsetZ": 0}

iterator = iter(sys.argv[1:])
value = next(iterator, None)
while not value is None:
    if value[0] == "-":
        if value[1:] in parameters:
            parameter = value[1:]
            value = next(iterator, None)
            if not value is None:
                parameters[parameter] = value
    value = next(iterator, None)


''' Start Processing '''

if not parameters["pic"] is None and os.path.isdir(parameters["pic"]):
    if not parameters["offsetZ"] is None:
        print("offset of " + parameters["offsetZ"] + "m defined in z axis")

    lst_pictures = importPictureNames(parameters["pic"])
    if not parameters["justin"] is None and os.path.isfile(parameters["justin"]):
        lst_event = importJustinFiles(parameters["justin"], float(parameters["offsetZ"]))
        print("Justinfile imported")
    elif not parameters["cam"] is None and os.path.isfile(parameters["cam"]):
        lst_event = importCamFiles(parameters["cam"], float(parameters["offsetZ"]))
        print("Camfile imported")
    else:
        raise Exception("Event Parameter missing")

    lst_matched = matchPicturWithEvents(lst_event, lst_pictures, skipPictures=int(parameters["skp"]), skipEvents=int(parameters["ske"]))

    if not parameters["hex"] is None and os.path.isfile(parameters["hex"]):
        if not (parameters["lx"] == 0 and parameters["ly"] == 0 and parameters["lz"] == 0):
            leverarm = (parameters["lx"], parameters["ly"], parameters["lz"])

            lst_hexalog = importHexalogFiles(parameters["hex"])
            print("Hexalogfile imported")
            matchWithHexalogs(lst_matched, lst_hexalog, skipHexalogs=int(parameters["skh"]))
            if not parameters["justin"] is None:
                matchLeverArmWithJustin(lst_matched, leverarm)
            elif not parameters["cam"] is None:
                matchLeverArmWithCam(lst_matched, leverarm)
        else:
            print("leverarm is not defined, set lx, ly or/and lz parameter", file=sys.stderr)
    else:
        print("Hexalogfile missing")

    if not parameters["acc"] is None:
        matchWithAccuracy(lst_matched, float(parameters["acc"]))
        print("Accuracy overwritten")

    if not parameters["o"] is None:
        exportMatched(lst_matched, parameters["o"])
    else:
        print("Export-Path missing")
        for row in lst_matched:
            print(row)

else:
    raise Exception("Picture Path missing")