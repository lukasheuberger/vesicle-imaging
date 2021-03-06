"""Basic czi image handling and information extration."""


import czifile
import os
import xml.etree.ElementTree as ET
from vesicle_imaging import imgfileutils as imf


def get_files(path: str):
    files = []
    filenames = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        f.sort()
        for file in f:
            if '.czi' in file:
                filenames.append(file)
                file_path = os.path.join(r, file)
                files.append(file_path)
    return files, filenames

def write_metadata_xml(path: str, files: list):
    try:
        metadata_path = ''.join([path, '/metadata'])
        print(metadata_path)
        os.mkdir(metadata_path)
    except FileExistsError:
        pass

    for file in files:
        print(file)
        xmlczi = czifile.CziFile(file).metadata()

        # define the new filename for the XML to be created later
        # split string at last / and add folder
        xmlfile = file.replace('.czi', '_CZI_MetaData.xml')
        xmlfile, filename = xmlfile.rsplit('/', 1)
        xmlfile = ''.join([xmlfile, '/metadata/', filename])

        # xmlfile = ''.join(['metadata/',xmlfile])

        # get the element tree
        tree = ET.ElementTree(ET.fromstring(xmlczi))

        # write xml to disk
        tree.write(xmlfile, encoding='utf-8', method='xml')

        print('Write special CZI XML metainformation for: ', xmlfile)

def load_image_data(files: list):
    all_img_data = []
    all_metadata = []
    all_add_metadata = []

    for file in files:
    # get the array and the metadata
        print (file)
        img_data, metadata, add_metadata = imf.get_array_czi(file, return_addmd=False)
        all_img_data.append(img_data)
        all_metadata.append(metadata)
        all_add_metadata.append(add_metadata)
    return all_img_data, all_metadata, all_add_metadata

def extract_channels_xy(img_data: list):
    img_xy_data = []
    for index, img in enumerate(img_data):
        channels_xy = []
        for image in img:
            channels_xy.append(image[0, 0, :, 0, 0, :, :])
        img_xy_data.append(channels_xy)
    print ('image XY data extracted')
    return img_xy_data

def extract_channels_timelapse(img_data):
    channels_timelapse = []
    for image in img_data:
        channels_timelapse.append(image[0, 0, :, :, 0, :, :])
    return channels_timelapse

def disp_channels(add_metadata):
    # channels are the same for both conditions
    channel_names = []
    dyes = []
    add_metadata_detectors = \
    add_metadata[0]['Experiment']['ExperimentBlocks']['AcquisitionBlock']['MultiTrackSetup']['TrackSetup'][
        'Detectors']['Detector']
    # channels of all images are the same so image 0 taken
    for channel in add_metadata_detectors:
        print(channel['ImageChannelName'])
        print(channel['Dye'])
        dyes.append(channel['Dye'])
        channel_name = ' '.join([channel['ImageChannelName'], str(channel['Dye'])])
        print(channel_name)
        channel_names.append(channel_name)
        print('------------------------------------')
    return dyes

def disp_all_metadata(metadata):
    # show all the metadata
    for index, image in enumerate(metadata):
        for key, value in image[0].items():
            # print all key-value pairs for the dictionary
            print(key, ' : ', value)
        print('------------------------------------')

def disp_basic_img_info(img_data, img_metadata):
    for index, img in enumerate(img_data):
        image = img[0]
        print('image', index + 1, ':')
        print('Image: ', img_metadata[index][0]['Filename'])
        print('CZI Array Shape : ', img_metadata[index][0]['Shape'])
        print('CZI Dimension Entry : ', img_metadata[index][0]['Axes'])
        print('-----------------------------')

def disp_channels(img_add_metadata, type):
    if type == 'SingleTrack':
        # channels are the same for all conditions
        channels = []
        add_metadata_detectors = \
        img_add_metadata[0][0]['Experiment']['ExperimentBlocks']['AcquisitionBlock']['MultiTrackSetup']['TrackSetup']['Detectors']['Detector']
        print (add_metadata_detectors)
        # channels of all images are the same so image 0 taken
        for channel in add_metadata_detectors:
            #print (channel)
            print(channel['ImageChannelName'])
            print(channel['Dye'])
            # channel_name = ' '.join([channel['ImageChannelName'],str(channel['Dye'])])
            # print (channel_name)
            if channel['Dye'] is not None:
                channel_name = channel['Dye'].replace(' ', '_')
                channel_name = channel_name.replace('/', '-')
                channels.append(channel_name)
            else:
                channels.append('Vis')
            print('-------------------------------------')
        print(channels)
    if type == 'MultiTrack':
        # channels are the same for all conditions
        channels = []
        add_metadata_detectors = \
            img_add_metadata[0][0]['Experiment']['ExperimentBlocks']['AcquisitionBlock']['MultiTrackSetup'][
                'TrackSetup']  # ['Detectors']['Detector']
        # print (add_metadata_detectors)
        for track in add_metadata_detectors:
            detector_data = track['Detectors']['Detector']
            #print(detector_data)
            # channels of all images are the same so image 0 taken
            #print(len(detector_data))
            if len(
                    detector_data) < 4:  # len of dict itself is ~25, so 4 is chosen so a 3 wavelength track could be used
                for channel in detector_data:
                    print(channel['ImageChannelName'])
                    print(channel['Dye'])
                    # channel_name = ' '.join([channel['ImageChannelName'],str(channel['Dye'])])
                    # print (channel_name)
                    if channel['Dye'] is not None:
                        channel_name = channel['Dye'].replace(' ', '_')
                        channel_name = channel_name.replace('/', '-')
                        channels.append(channel_name)
                    else:
                        channels.append('Vis')
                    print('------------------------------------')
            else:
                print(detector_data['ImageChannelName'])
                print(detector_data['Dye'])
                # channel_name = ' '.join([channel['ImageChannelName'],str(channel['Dye'])])
                # print (channel_name)
                if detector_data['Dye'] is not None:
                    channel_name = detector_data['Dye'].replace(' ', '_')
                    channel_name = channel_name.replace('/', '-')
                    channels.append(channel_name)
                else:
                    channels.append('Vis')
                print('------------------------------------')
        print(channels)
        return channels

def disp_scaling(img_add_metadata):
    scaling_x = []
    for index, image in enumerate(img_add_metadata):
        scale = image[0]['Experiment']['ExperimentBlocks']['AcquisitionBlock']['AcquisitionModeSetup']['ScalingX']
        scaling_x.append(scale)
    # print('scale factor: ', scaling_x)
    return scaling_x
