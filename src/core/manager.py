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
        :param scale_bar_mask_path:
        :param scale_bar_length:
        :return:
        """

        image_raw: np.ndarray = plt.imread(scale_bar_mask_path)
        row_of_column_maxes: np.ndarray = image_raw.max(0)
        indices = np.where(row_of_column_maxes[:, 0] == max(row_of_column_maxes[:, 0]))[0]

        scale_bar_pixels = max(indices) - min(indices) + 1

        factor = scale_bar_length / scale_bar_pixels

        for slide in self.slides:
            slide.scale(factor)

    def build_file_structure(self):
        # Builds folders and copies files
        pass
        # for slide in map
        #
        #
        # os.path.split(data_path)
        # path.split('_')

    def populate(self):
        pass
        # Reads in the known files








