import os
from typing import List
import matplotlib.pyplot as plt
import numpy as np
import shutil

from src.core import Slide, Map, Fascicle, Nerve
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

                if directory_part == sample:
                    scale_source_file = os.path.join(start_directory, *source_directory, MaskFileNames.SCALE_BAR.value)
                    if os.path.exists(scale_source_file):
                        shutil.copy2(scale_source_file, MaskFileNames.SCALE_BAR.value)
                    else:
                        raise Exception('s.tif not found')

            for target_file in [item.value for item in MaskFileNames if item != MaskFileNames.SCALE_BAR]:
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

    def populate(self, mask_input_mode: MaskInputMode, nerve_mode: NerveMode):

        def exists(mask_file_name: MaskFileNames)
            return os.path.exists(mask_file_name.value)

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

            if not os.path.exists(MaskFileNames.RAW.value):
                self.throw(18)
            elif not os.path.exists(MaskFileNames.SCALE_BAR.value):
                self.throw(19)

            # init fascicles list
            fascicles: List[Fascicle] = []

            # load fascicles and check that the files exist
            if mask_input_mode == MaskInputMode.INNERS:
                if exists(MaskFileNames.INNERS.value):
                    fascicles = Fascicle.inner_to_list(MaskFileNames.INNERS.value,
                                                       self.configs[ConfigKey.EXCEPTIONS.value])
                else:
                    self.throw(21)

            elif mask_input_mode == MaskInputMode.OUTERS:
                #fascicles = Fascicle.outer_to_list(MaskFileNames.OUTERS.value, self.configs[ConfigKey.EXCEPTIONS.value])
                self.throw(20)

            elif mask_input_mode == MaskInputMode.INNER_AND_OUTER_SEPARATE:
                if exists(MaskFileNames.INNERS.value) and exists(MaskFileNames.OUTERS.value):
                    fascicles = Fascicle.separate_to_list(MaskFileNames.INNERS.value,
                                                          MaskFileNames.OUTERS.value,
                                                          self.configs[ConfigKey.EXCEPTIONS.value])
                else:
                    self.throw(22)

            elif mask_input_mode == MaskInputMode.INNER_AND_OUTER_COMPILED:
                if exists(MaskFileNames.COMPILED.value):
                    fascicles = Fascicle.compiled_to_list(MaskFileNames.COMPILED.value,
                                                          self.configs[ConfigKey.EXCEPTIONS.value])
                else:
                    self.throw(23)

            else: # exhaustive
                pass


            # check nerve mode, if nerve mode is present, check that the nerve trace is there and load it in
            # if nerve mode is not present, check that list of fascicles is length of one, if not throw error.
            # if pass, nerve = Nerve(fascicles[0].outer.deepcopy())


            # and scale bar


            if nerve_mode == NerveMode.PRESENT:
                # check and load in nerve, throw error if not present

            elif nerve_mode == NerveMode.NOT_PRESENT:
                # compiled
                # nerve = copy of fasc
                #
            else:  # exhaustive
                pass


            # r.tif does not exist, fail

            # s.tif does not exist, fail

            # compiled, inner only, outer only, inner and outer

            #['r', 'f', 'i', 'o', 's']


            os.chdir(start_directory)










