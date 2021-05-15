import os, sys
import Metashape

# get parameter: directory path
input_folder = sys.argv[1:][0]
if os.path.isdir(input_folder):

    # create Chunk in Metashapeproject
    psx = Metashape.app.document
    chunk = psx.chunks[-1]

    # list images in input_folder
    image_list = os.listdir(input_folder)

    '''directory_list = list()
    for directory in image_list:
        if os.path.isdir(os.path.join(input_folder, directory)):
            directory_list.append(os.path.join(input_folder, directory))
        elif os.path.isfile(os.path.join(input_folder, directory)):
            raise Exception("")'''

    # add camera group with directoryname as label
    camera_group = chunk.addCameraGroup()
    camera_group_label = os.path.basename(input_folder)
    camera_group.label = camera_group_label

    # add first camera to cameragroup
    camera = chunk.addCamera()
    camera.group = camera_group
    camera.open(os.path.join(input_folder, image_list[0]))

    # create sensor of the cameragroup
    sensor = chunk.addSensor()
    sensor.label = camera.photo.meta['Exif/Model']
    sensor.type = Metashape.Sensor.Type.Frame

    # dimensions of the sensor
    sensor.width = camera.photo.image().width
    sensor.height = camera.photo.image().height

    # focal length an 35mm focal length
    sensor.focal_length = float(camera.photo.meta['Exif/FocalLength'])
    f35mmFocalLength = float(camera.photo.meta['Exif/FocalLengthIn35mmFilm'])
    sensor.pixel_height = float(36.0*sensor.focal_length/f35mmFocalLength/sensor.width)
    sensor.pixel_width = sensor.pixel_height
    camera.sensor = sensor

    # add images of the directory to the camera group
    for iCamera in range(1, len(image_list)):
        # create the camera
        camera = chunk.addCamera()
        camera.group = camera_group
        # loading photo to the camera instance
        camera.open(os.path.join(input_folder, image_list[iCamera]))
        camera.sensor = sensor

    print(str(len(image_list)) + " images added to camera group '" + camera_group_label + "' in chunk '" + str(chunk.label) + "'")

else:
    raise Exception("input parameter is not path to directory of images")