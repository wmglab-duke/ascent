from typing import List
import matplotlib.pyplot as plt
import numpy as np

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
        # Builds folders and copies files
        samples_path = self.path(ConfigKey.MASTER, 'samples_path')

        for slide_info in self.map.slides:
            cassette: str = slide_info.cassette




    def populate(self):
        # Reads in the known files
        for slide_info in self.map.slides:

            cassette:str = slide_info.cassette
            # make the path, read in

            slide_info.

        sample_path = self.path(ConfigKey.MASTER, 'samples_path')

        if exist(os.path.isdir)










