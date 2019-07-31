import os
from typing import List
import matplotlib.pyplot as plt
import numpy as np
import shutil

from src.core import Slide, Map
from src.utils import *


class Manager(Exceptionable, Configurable):

    def __init__(self, master_config: dict, exception_config: list, map_mode: SetupMode):

        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self, SetupMode.OLD, ConfigKey.MASTER, master_config)

        self.slides: List[Slide] = []

        self.map = Map(self.configs[ConfigKey.MASTER.value],
                       self.configs[ConfigKey.EXCEPTIONS.value],
                       map_mode)

    def scale(self, scale_bar_mask_path: str, scale_bar_length: float):
        """
        Scale all slides to the correct unit.
        :param scale_bar_mask_path: path to binary mask with white straight scale bar
        :param scale_bar_length: length (in global units as determined by config/user) of the scale bar
        """
        # load in image
        image_raw: np.ndarray = plt.imread(scale_bar_mask_path)
        # get maximum of each column (each "pixel" is a 4-item vector)
        row_of_column_maxes: np.ndarray = image_raw.max(0)
        # find the indices of columns in original image where the first pixel item was maxed (i.e. white)
        indices = np.where(row_of_column_maxes[:, 0] == max(row_of_column_maxes[:, 0]))[0]
        # find the length of the scale bar by finding total range of "max white" indices
        scale_bar_pixels = max(indices) - min(indices) + 1
        # calculate scale factor as unit/pixel
        factor = scale_bar_length / scale_bar_pixels
        # for each slide, scale to units
        for slide in self.slides:
            slide.scale(factor)

    def build_file_structure(self):
        # TODO: ADD DOCUMENTATION

        # get starting point so able to go back
        start_directory: str = os.getcwd()
        # go to samples root
        samples_path: str = self.path(ConfigKey.MASTER, 'samples_path')

        # get sample name
        sample: str = self.search(ConfigKey.MASTER, 'sample')

        # loop through each slide
        for slide_info in self.map.slides:
            # unpack data and force cast to string
            cassette, number, _, source_directory = slide_info.data()
            cassette, number = (str(item) for item in (cassette, number))

            for directory_part in samples_path, sample, cassette, number, 'masks':
                if not os.path.exists(directory_part):
                    os.makedirs(directory_part)
                os.chdir(directory_part)

            for letter_code in ['r', 'f', 'i', 'o', 's']:
                target_file = letter_code + '.tif'
                source_file = os.path.join(start_directory,
                                           *source_directory,
                                           '_'.join([sample, cassette, number, target_file]))
                print('source: {}\ntarget: {}'.format(source_file, target_file))
                if os.path.exists(source_file):
                    print('\tFOUND\n')
                    shutil.copy2(source_file, target_file)
                else:
                    print('\tNOT FOUND\n')

            os.chdir(start_directory)

    def populate(self):

        # get starting point so able to go back
        start_directory: str = os.getcwd()

        samples_path = self.path(ConfigKey.MASTER, 'samples_path')

        # get sample name
        sample: str = self.search(ConfigKey.MASTER, 'sample')

        for slide_info in self.map.slides:
            # unpack data and force cast to string
            cassette, number, position, _ = slide_info.data()
            cassette, number = (str(item) for item in (cassette, number))

            os.chdir(os.path.join(samples_path, sample, cassette, number, 'masks'))



            ['r', 'f', 'i', 'o', 's']


            os.chdir(start_directory)


            # Reads in the known files
            # check if i and o exist

            #os.path.join(samples_path, cassette, 'r.tif')
            #r s n









