#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

# builtins
import os
import shutil
import subprocess
from typing import List, Tuple, Union

# packages
import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys
import warnings
from scipy.ndimage.morphology import binary_fill_holes
from shapely.geometry import LineString
from skimage import morphology

# ascent
from src.core import Slide, Map, Fascicle, Nerve, Trace
from src.utils import Exceptionable, Configurable, Saveable, SetupMode, Config, MaskFileNames, NerveMode, \
    MaskInputMode, ReshapeNerveMode, DeformationMode, PerineuriumThicknessMode, WriteMode, CuffInnerMode, \
    TemplateOutput, TemplateMode, ScaleInputMode, ShrinkageMode
from .deformable import Deformable


class Sample(Exceptionable, Configurable, Saveable):
    """
    Required (Config.) JSON's:
        SAMPLE
        RUN
    """

    def __init__(self, exception_config: list):
        """
        :param master_config: preloaded configuration data for master
        :param exception_config: preloaded configuration data for exceptions
        :param map_mode: setup mode. If you want to build a new map from a directory, then NEW. Otherwise, or if for
        a single slide, OLD.
        """

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

        # Initialize slides
        self.slides: List[Slide] = []

        # Set instance variable map
        self.map = None

        # Set instance variable morphology
        self.morphology = dict()

        # Add JSON for perineurium thickness relationship with nerve morphology metrics -- used to calculate contact impedances if "use_ci" is True
        self.add(SetupMode.NEW, Config.CI_PERINEURIUM_THICKNESS, os.path.join('config',
                                                                              'system',
                                                                              'ci_peri_thickness.json'))

    def init_map(self, map_mode: SetupMode) -> 'Sample':
        """
        Initialize the map. NOTE: the Config.SAMPLE json must have been externally added.
        :param map_mode: should be old for now, but keeping as parameter in case needed in future
        """
        if Config.SAMPLE.value not in self.configs.keys():
            self.throw(38)

        # Make a slide map
        self.map = Map(self.configs[Config.EXCEPTIONS.value])
        self.map.add(SetupMode.OLD, Config.SAMPLE, self.configs[Config.SAMPLE.value])
        self.map.init_post_config(map_mode)

        return self

    def scale(self, factor) -> 'Sample':
        """
        Scale all slides to the correct unit.
        :param factor: factor by which to scale the image (1=no change)
        """
        for slide in self.slides:
            slide.scale(factor)

        return self

    def smooth(self, n_distance, i_distance) -> 'Sample':
        """
        Smooth traces for all slides
        :param n_distance: distance to inflate and deflate the nerve trace
        :param i_distance: distance to inflate and deflate the fascicle traces
        """
        for slide in self.slides:
            slide.smooth_traces(n_distance, i_distance)

        return self

    def generate_perineurium(self, fit: dict) -> 'Sample':
        """
        Adds perineurium to inners
        """
        for slide in self.slides:
            slide.generate_perineurium(fit)

        return self

    def im_preprocess(self, path):
        """
        Performs cleaning operations on the input image
        :param path: path to image which will be processed
        """
        img = cv2.imread(path, -1)

        if self.search(Config.SAMPLE, 'image_preprocessing', 'fill_holes', optional=True) == True:
            if self.search_mode(MaskInputMode, Config.SAMPLE) == MaskInputMode.INNER_AND_OUTER_COMPILED:
                print(
                    'WARNING: Skipping fill holes since MaskInputMode is INNER_AND_OUTER_COMPILED. Change fill_holes to False to suppress this warning.')
            else:
                img = binary_fill_holes(img)
        removal_size = self.search(Config.SAMPLE, 'image_preprocessing', 'object_removal_area', optional=True)
        if removal_size:
            if removal_size < 0: self.throw(119)
            img = morphology.remove_small_objects(img, removal_size)
        cv2.imwrite(path, img.astype(int) * 255)

    def get_factor(self, scale_bar_mask_path: str, scale_bar_length: float, scale_bar_is_literal: bool) -> 'Sample':
        """
        Returns scaling factor (micrometers per pixel)
        :param scale_bar_mask_path: path to binary mask with white straight (horizontal) scale bar
        :param scale_bar_length: length (in global units as determined by config/user) of the scale bar
        """

        if scale_bar_is_literal:
            # use explicitly specified um/px scale instead of drawing from a scale bar image
            factor = scale_bar_length
        else:
            # load in image
            image_raw: np.ndarray = cv2.imread(scale_bar_mask_path)

            # get maximum of each column (each "pixel" is a 4-item vector)
            row_of_column_maxes: np.ndarray = image_raw.max(0)
            # find the indices of columns in original image where the first pixel item was maxed (i.e. white)

            if row_of_column_maxes.ndim == 2:  # masks from histology, 3 or 4 bit
                indices = np.where(row_of_column_maxes[:, 0] == max(row_of_column_maxes[:, 0]))[0]
            elif row_of_column_maxes.ndim == 1:  # masks from mock morphology, 1 bit
                indices = np.where(row_of_column_maxes[:] == max(row_of_column_maxes[:]))[0]
            else:
                # may need to expand here in future?
                self.throw(97)

            # find the length of the scale bar by finding total range of "max white" indices
            scale_bar_pixels = max(indices) - min(indices) + 1

            # calculate scale factor as unit/pixel
            factor = scale_bar_length / scale_bar_pixels

        return factor

    def build_file_structure(self, printing: bool = False) -> 'Sample':
        """
        :param printing: bool, gives user console output
        """
        scale_input_mode = self.search_mode(ScaleInputMode, Config.SAMPLE, optional=True)
        # For backwards compatibility, if scale mode is not specified assume a mask image is provided
        if scale_input_mode is None:
            scale_input_mode = ScaleInputMode.MASK

        sample_index = self.search(Config.RUN, 'sample')

        # get starting point so able to go back
        start_directory: str = os.getcwd()

        # go to samples root
        samples_path = self.path(Config.SAMPLE, 'samples_path')

        # get sample NAME
        sample: str = self.search(Config.SAMPLE, 'sample')

        # ADDITION: if only one slide present, check if names abide by <NAME>_0_0_<CODE>.tif format
        #           if not abiding, rename files so that they abide
        if len(self.map.slides) == 1:
            #print('Renaming input files to conform with map input interface where necessary.')
            source_dir = os.path.join(*self.map.slides[0].data()[3])
            source_files = os.listdir(source_dir)
            for mask_fname in [f.value for f in MaskFileNames if f.value in source_files]:
                shutil.move(
                    os.path.join(source_dir, mask_fname),
                    os.path.join(source_dir, '{}_0_0_{}'.format(sample, mask_fname))
                )
        else:
            self.throw(96)

        # loop through each slide
        for slide_info in self.map.slides:
            # unpack data and force cast to string
            cassette, number, _, source_directory = slide_info.data()
            cassette, number = (str(item) for item in (cassette, number))

            scale_was_copied = False
            for directory_part in samples_path, str(sample_index), 'slides', cassette, number, 'masks':

                if not os.path.exists(directory_part):
                    os.makedirs(directory_part)
                os.chdir(directory_part)
                if scale_input_mode == ScaleInputMode.MASK:
                    # only try to copy scale image if it is being used
                    if (directory_part == str(sample_index)) and not scale_was_copied:
                        scale_source_file = os.path.join(start_directory,
                                                         *source_directory,
                                                         '_'.join([sample,
                                                                   cassette,
                                                                   number,
                                                                   MaskFileNames.SCALE_BAR.value]))
                        if os.path.exists(scale_source_file):
                            shutil.copy2(scale_source_file, MaskFileNames.SCALE_BAR.value)
                        else:
                            print('ERROR: scale_source_file: {} not found'.format(scale_source_file))
                            self.throw(98)

                        scale_was_copied = True

            for target_file in [item.value for item in MaskFileNames if item != MaskFileNames.SCALE_BAR]:
                source_file = os.path.join(start_directory,
                                           *source_directory,
                                           '_'.join([sample, cassette, number, target_file]))
                if printing:
                    print('source: {}\ntarget: {}'.format(source_file, target_file))
                if os.path.exists(source_file):
                    if printing:
                        print('\tFOUND\n')
                    shutil.copy2(source_file, target_file)
                else:
                    if printing:
                        print('\tNOT FOUND\n')

            os.chdir(start_directory)

            return self

    def populate(self, deform_animate: bool = True) -> 'Sample':
        """
        :param deform_animate: boolean indicating whether to show nerve deformation
        :return:
        """

        # get parameters (modes) from configuration file
        mask_input_mode = self.search_mode(MaskInputMode, Config.SAMPLE)
        nerve_mode = self.search_mode(NerveMode, Config.SAMPLE)
        reshape_nerve_mode = self.search_mode(ReshapeNerveMode, Config.SAMPLE)
        deform_mode = self.search_mode(DeformationMode, Config.SAMPLE)
        deform_ratio = None
        scale_input_mode = self.search_mode(ScaleInputMode, Config.SAMPLE, optional=True)
        plot = self.search(Config.SAMPLE, 'plot', optional=True)
        plot_folder = self.search(Config.SAMPLE, 'plot_folder', optional=True)
        # For backwards compatibility, if scale mode is not specified assume a mask image is provided
        if scale_input_mode is None:
            scale_input_mode = ScaleInputMode.MASK

        def exists(mask_file_name: MaskFileNames):
            return os.path.exists(mask_file_name.value)

        # get starting point so able to go back
        start_directory: str = os.getcwd()

        # get sample name
        sample: str = str(self.search(Config.RUN, 'sample'))

        # create scale bar path
        if scale_input_mode == ScaleInputMode.MASK:
            scale_path = os.path.join('samples', sample, MaskFileNames.SCALE_BAR.value)
        elif scale_input_mode == ScaleInputMode.RATIO:
            scale_path = ''
        else:
            self.throw(108)

        plotpath = os.path.join('samples', str(sample), 'plots')
        if not os.path.exists(plotpath):
            os.makedirs(plotpath)

        for slide_info in self.map.slides:

            orientation_centroid: Union[Tuple[float, float], None] = None

            # unpack data and force cast to string
            cassette, number, position, _ = slide_info.data()
            cassette, number = (str(item) for item in (cassette, number))

            os.chdir(os.path.join('samples', str(sample), 'slides', cassette, number, 'masks'))

            # convert any TIFF to TIF
            proc = None
            if any(fname.endswith('.tiff') for fname in os.listdir('.')):
                if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
                    proc = subprocess.Popen(['bash',
                                             'for file in *.tiff; do mv "$file" "${file%.tiff}.tif"; done'])
                else:
                    proc = subprocess.Popen(['powershell.exe',
                                             'Dir | Rename-Item –NewName { $_.name –replace “.tiff“,”.tif” }'])
                proc.wait()

            if not exists(MaskFileNames.RAW):
                print('No raw tif found, but continuing. (Sample.populate)')
                # self.throw(18)

            if exists(MaskFileNames.ORIENTATION):

                img = np.flipud(cv2.imread(MaskFileNames.ORIENTATION.value, -1))

                if len(img.shape) > 2 and img.shape[2] > 1:
                    img = img[:, :, 0]

                contour, _ = cv2.findContours(img,
                                              cv2.RETR_TREE,
                                              cv2.CHAIN_APPROX_SIMPLE)
                if len(contour) > 1: self.throw(124)
                if len(contour) < 1: self.throw(125)
                trace = Trace([point + [0] for point in contour[0][:, 0, :]], self.configs[Config.EXCEPTIONS.value])
                orientation_centroid = trace.centroid()
            else:
                print('No orientation tif found, but continuing. (Sample.populate)')

            # preprocess binary masks
            mask_dims = []
            for mask in ["COMPILED", "INNERS", "OUTERS", "NERVE", "ORIENTATION"]:
                maskfile = getattr(MaskFileNames, mask)
                if exists(maskfile):
                    mask_dims.append(cv2.imread(getattr(maskfile, 'value')).shape)
                    self.im_preprocess(getattr(maskfile, 'value'))
            if len(mask_dims) == 0: self.throw(121)
            if not np.all(np.array(mask_dims) == mask_dims[0]): self.throw(122)
            scalemask = getattr(MaskFileNames, "SCALE_BAR")
            if exists(scalemask):
                mask_dims.append(cv2.imread(getattr(scalemask, 'value')).shape)
                if not np.all(np.array(mask_dims) == mask_dims[0]): print(
                    'WARNING: Scale bar mask has a different resolution than morphology masks. \nProgram will continue and assume that the scale bar mask microns/pixel ratio is correct.')
            # fascicles list
            fascicles: List[Fascicle] = []

            # load fascicles and check that the files exist, then generate fascicles
            if mask_input_mode == MaskInputMode.INNERS:

                if exists(MaskFileNames.INNERS):
                    fascicles = Fascicle.to_list(MaskFileNames.INNERS.value, None,
                                                 self.configs[Config.EXCEPTIONS.value])
                else:
                    self.throw(21)

            elif mask_input_mode == MaskInputMode.OUTERS:
                # fascicles = Fascicle.outer_to_list(MaskFileNames.OUTERS.value,
                #                                    self.configs[Config.EXCEPTIONS.value])
                self.throw(20)

            elif mask_input_mode == MaskInputMode.INNER_AND_OUTER_SEPARATE:
                if exists(MaskFileNames.INNERS) and exists(MaskFileNames.OUTERS):
                    fascicles = Fascicle.to_list(MaskFileNames.INNERS.value,
                                                 MaskFileNames.OUTERS.value,
                                                 self.configs[Config.EXCEPTIONS.value])
                else:
                    self.throw(22)

            elif mask_input_mode == MaskInputMode.INNER_AND_OUTER_COMPILED:
                if exists(MaskFileNames.COMPILED):
                    # first generate outer and inner images
                    i_image = os.path.split(MaskFileNames.COMPILED.value)[0] + 'i_from_c.tif'
                    o_image = os.path.split(MaskFileNames.COMPILED.value)[0] + 'o_from_c.tif'
                    self.io_from_compiled(MaskFileNames.COMPILED.value, i_image, o_image)
                    # then get fascicles
                    fascicles = Fascicle.to_list(i_image, o_image, self.configs[Config.EXCEPTIONS.value])
                else:
                    self.throw(23)

            else:  # exhaustive
                pass

            nerve = None
            if nerve_mode == NerveMode.PRESENT:
                # check and load in nerve, throw error if not present

                if exists(MaskFileNames.NERVE):
                    img_nerve = cv2.imread(MaskFileNames.NERVE.value, -1)

                    if len(img_nerve.shape) > 2 and img_nerve.shape[2] > 1:
                        img_nerve = img_nerve[:, :, 0]

                    contour, _ = cv2.findContours(np.flipud(img_nerve),
                                                  cv2.RETR_TREE,
                                                  cv2.CHAIN_APPROX_SIMPLE)
                    nerve = Nerve(Trace([point + [0] for point in contour[0][:, 0, :]],
                                        self.configs[Config.EXCEPTIONS.value]))

            if len(fascicles) > 1 and nerve_mode != NerveMode.PRESENT:
                self.throw(110)

            slide: Slide = Slide(fascicles,
                                 nerve,
                                 nerve_mode,
                                 self.configs[Config.EXCEPTIONS.value],
                                 will_reposition=(deform_mode != DeformationMode.NONE))

            # get orientation angle (used later to calculate pos_ang for model.json)
            if orientation_centroid is not None:
                # logic updated 10/11/2021

                # choose outer (based on if nerve is present)
                outer = slide.nerve if (slide.nerve is not None) else slide.fascicles[0].outer

                # create line between outer centroid and orientation centroid
                outer_x, outer_y = outer.centroid()
                ori_x, ori_y = orientation_centroid

                # set orientation_angle
                slide.orientation_angle = np.arctan2(ori_y - outer_y, ori_x - outer_x)

            # shrinkage correction
            s_mode = self.search_mode(ShrinkageMode, Config.SAMPLE, optional=True)
            s_pre = self.search(Config.SAMPLE, "scale", "shrinkage")
            if s_mode is None:
                print('WARNING: ShrinkageMode in Config.Sample is not defined or mode provided is not a known option. '
                      'Proceeding with backwards compatible (i.e., original default functionality) of LENGTH_FORWARDS'
                      ' shrinkage correction.\n')
                shrinkage_correction = 1 + s_pre
            else:
                shrinkage_correction = None
                if s_mode == ShrinkageMode.LENGTH_BACKWARDS:
                    shrinkage_correction = 1 / (1 - s_pre)
                elif s_mode == ShrinkageMode.LENGTH_FORWARDS:
                    shrinkage_correction = s_pre + 1
                elif s_mode == ShrinkageMode.AREA_BACKWARDS:
                    shrinkage_correction = 1 / np.sqrt(1 - s_pre)
                elif s_mode == ShrinkageMode.AREA_FORWARDS:
                    shrinkage_correction = np.sqrt(1 + s_pre)
                else:
                    self.throw(134)

            if shrinkage_correction < 1:
                self.throw(133)

            slide.scale(shrinkage_correction)

            self.slides.append(slide)

            os.chdir(start_directory)

        # get scaling factor (to convert from pixels to microns)
        if os.path.exists(scale_path) and scale_input_mode == ScaleInputMode.MASK:
            factor = self.get_factor(scale_path, self.search(Config.SAMPLE, 'scale', 'scale_bar_length'), False)
        elif scale_input_mode == ScaleInputMode.RATIO:
            factor = self.get_factor(scale_path, self.search(Config.SAMPLE, 'scale', 'scale_ratio'), True)
        else:
            print(scale_path)
            self.throw(19)

        # scale to microns
        self.scale(factor)

        if plot == True:
            plt.figure()
            slide.plot(final=False, fix_aspect_ratio='True', axlabel=u"\u03bcm",
                       title='Initial sample from morphology masks')
            if plot_folder == True:
                plt.savefig(plotpath + '/sample_initial')
                plt.clf()
                plt.close('all')
            else:
                plt.show()

        # get smoothing params
        n_distance = self.search(Config.SAMPLE, 'smoothing', 'nerve_distance', optional=True)
        i_distance = self.search(Config.SAMPLE, 'smoothing', 'fascicle_distance', optional=True)
        # smooth traces
        if not (n_distance == i_distance == None):
            if nerve_mode == NerveMode.PRESENT and n_distance is None:
                self.throw(112)
            else:
                self.smooth(n_distance, i_distance)

        # after scaling, if only inners were provided, generate outers
        if mask_input_mode == MaskInputMode.INNERS:
            peri_thick_mode: PerineuriumThicknessMode = self.search_mode(PerineuriumThicknessMode,
                                                                         Config.SAMPLE)

            perineurium_thk_info: dict = self.search(Config.CI_PERINEURIUM_THICKNESS,
                                                     PerineuriumThicknessMode.parameters.value,
                                                     str(peri_thick_mode).split('.')[-1])

            self.generate_perineurium(perineurium_thk_info)

        # repositioning!
        for i, slide in enumerate(self.slides):
            print('\tslide {} of {}'.format(1 + i, len(self.slides)))
            # title = ''

            if nerve_mode == NerveMode.NOT_PRESENT and deform_mode is not DeformationMode.NONE:
                self.throw(40)

            partially_deformed_nerve = None

            if deform_mode == DeformationMode.PHYSICS:
                print('\t\tsetting up physics')
                if 'morph_count' in self.search(Config.SAMPLE).keys():
                    morph_count = self.search(Config.SAMPLE, 'morph_count')
                else:
                    morph_count = 100

                if 'deform_ratio' in self.search(Config.SAMPLE).keys():
                    deform_ratio = self.search(Config.SAMPLE, 'deform_ratio')
                    print('\t\tdeform ratio set to {}'.format(deform_ratio))
                else:
                    self.throw(118)

                # title = 'morph count: {}'.format(morph_count)
                sep_fascicles = self.search(Config.SAMPLE, "boundary_separation", "fascicles")
                sep_nerve = None

                print('\t\tensuring minimum fascicle separation of {} um'.format(sep_fascicles))

                if 'nerve' in self.search(Config.SAMPLE, 'boundary_separation').keys():
                    sep_nerve = self.search(Config.SAMPLE, 'boundary_separation', 'nerve')
                    print('\t\tensuring minimum nerve:fascicle separation of {} um'.format(sep_nerve))
                
                #scale nerve trace down by sep nerve, will be scaled back up later
                pre_area = slide.nerve.area()
                slide.nerve.offset(distance = -sep_nerve)
                slide.nerve.scale(1)
                slide.nerve.points = np.flip(slide.nerve.points,axis = 0) # set points to opencv orientation

                
                deformable = Deformable.from_slide(slide, ReshapeNerveMode.CIRCLE)

                movements, rotations = deformable.deform(morph_count=morph_count,
                                                         render=deform_animate,
                                                         minimum_distance=sep_fascicles,
                                                         ratio=deform_ratio)

                partially_deformed_nerve = Deformable.deform_steps(deformable.start,
                                                                   deformable.end,
                                                                   morph_count,
                                                                   deform_ratio)[-1]

                for move, angle, fascicle in zip(movements, rotations, slide.fascicles):
                    fascicle.shift(list(move) + [0])
                    fascicle.rotate(angle)

            elif deform_mode == DeformationMode.JITTER:
                slide.reposition_fascicles(slide.reshaped_nerve(reshape_nerve_mode), 10)
            else:  # must be DeformationMode.NONE
                import warnings

                if 'nerve' in self.search(Config.SAMPLE, 'boundary_separation').keys():
                    sep_nerve = self.search(Config.SAMPLE, 'boundary_separation', 'nerve')
                if sep_nerve != 0:
                    warnings.warn(
                        'NO DEFORMATION is happening! AND sep_nerve is not 0, sep_nerve = {}'.format(sep_nerve))
                else:
                    warnings.warn('NO DEFORMATION is happening!')

            if nerve_mode is NerveMode.PRESENT and deform_mode != DeformationMode.NONE:
                if deform_ratio != 1 and partially_deformed_nerve is not None:
                    partially_deformed_nerve.shift(-np.asarray(list(partially_deformed_nerve.centroid()) + [0]))
                    slide.nerve = partially_deformed_nerve
                    slide.nerve.offset(distance=sep_nerve)
                else:
                    slide.nerve = slide.reshaped_nerve(reshape_nerve_mode)
                #deforms+offsets usually shrinks the area a bit, so reset back to the original area
                if slide.nerve.area()<pre_area:
                    slide.nerve.scale((pre_area/slide.nerve.area())**.5)
                else:
                    print('Note: nerve area before deformation was {}, post deformation is {}'.format(
                        pre_area, self.nerve.area()))

            # shift slide about (0,0)
            slide.move_center(np.array([0, 0]))

            # Generate orientation point so src/core/query.py is happy
            if slide.orientation_angle is not None:
                # choose outer (based on if nerve is present)
                outer = slide.nerve if (slide.nerve is not None) else slide.fascicles[0].outer

                length = outer.mean_radius() * 10

                o_pt = np.array([np.cos(slide.orientation_angle), np.sin(slide.orientation_angle)]) * length

                ray = LineString([outer.centroid(), o_pt])

                # find intersection point with outer (interpolated)
                slide.orientation_point = np.array(ray.intersection(outer.polygon().boundary))
            
            #ensure that nothing went wrong in slide processing
            slide.validation()

        # scale with ratio = 1 (no scaling happens, but connects the ends of each trace to itself)
        self.scale(1)

        # slide.plot(fix_aspect_ratio=True, title=title)

        if plot == True:
            plt.figure()
            slide.plot(final=False, fix_aspect_ratio='True', axlabel=u"\u03bcm",
                       title='Final sample after any user specified processing')
            if plot_folder == True:
                plt.savefig(plotpath + '/sample_final')
                plt.clf()
                plt.close()
            else:
                plt.show()

            # plt.figure(2)
            # slide.nerve.plot()
            # plt.plot(*tuple(slide.nerve.points[slide.orientation_point_index][:2]), 'b*')
            # plt.show()

        return self

    def io_from_compiled(self, imgin, i_out, o_out):
        """
        Generate inner and outer mask from compiled mask
        :param imgin: path to input image (hint: c.tif)
        :param i_out: full path to desired output inner mask
        :param o_out: full path to desired output outer mask
        """
        compiled = cv2.imread(imgin, -1)

        imgnew = cv2.bitwise_not(compiled)

        h, w = imgnew.shape[:2]

        mask = np.zeros((h + 2, w + 2), np.uint8)

        cv2.floodFill(imgnew, mask, (0, 0), 0);

        cv2.imwrite(i_out, imgnew)

        cv2.imwrite(o_out, compiled + imgnew)

    def write(self, mode: WriteMode) -> 'Sample':
        """
        Write entire list of slides.
         """

        # get starting point so able to go back
        start_directory: str = os.getcwd()

        # get path to sample slides
        sample_path = os.path.join(self.path(Config.SAMPLE, 'samples_path'),
                                   str(self.search(Config.RUN, 'sample')),
                                   'slides')

        # loop through the slide info (index i SHOULD correspond to slide in self.slides)
        for i, slide_info in enumerate(self.map.slides):
            # unpack data and force cast to string
            cassette, number, _, source_directory = slide_info.data()
            cassette, number = (str(item) for item in (cassette, number))

            # build path to slide and ensure that it exists before proceeding
            slide_path = os.path.join(sample_path, cassette, number)
            if not os.path.exists(slide_path):
                self.throw(27)
            else:
                # change directories to slide path
                os.chdir(slide_path)

                # build the directory for output (name is the write mode)
                directory_to_create = ''
                if mode == WriteMode.SECTIONWISE2D:
                    directory_to_create = 'sectionwise2d'
                elif mode == WriteMode.SECTIONWISE:
                    directory_to_create = 'sectionwise'
                else:
                    self.throw(28)
                
                #clear directory if it exists, then create
                if os.path.exists(directory_to_create):
                    try:
                        shutil.rmtree(directory_to_create)
                    except:
                        pass
                try:
                    os.makedirs(directory_to_create)
                except:
                    pass
                
                os.chdir(directory_to_create)
                
                # WRITE
                self.slides[i].write(mode, os.getcwd())

            # go back up to start directory, then to top of loop
            os.chdir(start_directory)

        return self

    def make_electrode_input(self) -> 'Sample':

        # load template for electrode input
        electrode_input: dict = TemplateOutput.read(TemplateMode.ELECTRODE_INPUT)

        for cuff_inner_mode in CuffInnerMode:

            string_mode = str(cuff_inner_mode).split('.')[1]

            if cuff_inner_mode == CuffInnerMode.CIRCLE:

                (minx, miny, maxx, maxy) = self.slides[0].nerve.polygon().bounds
                electrode_input[string_mode]['r'] = max([(maxx - minx) / 2, (maxy - miny) / 2])

            elif cuff_inner_mode == CuffInnerMode.BOUNDING_BOX:

                (minx, miny, maxx, maxy) = self.slides[0].nerve.polygon().bounds
                electrode_input[string_mode]['x'] = maxx - minx
                electrode_input[string_mode]['y'] = maxy - miny

            else:
                pass

        # write template for electrode input
        TemplateOutput.write(electrode_input, TemplateMode.ELECTRODE_INPUT, self)

        return self

    def output_morphology_data(self) -> 'Sample':

        nerve_mode = self.search_mode(NerveMode, Config.SAMPLE)

        fascicles = [fascicle.morphology_data() for fascicle in self.slides[0].fascicles]

        if nerve_mode == NerveMode.PRESENT:
            nerve = Nerve.morphology_data(self.slides[0].nerve)
            morphology_input = {"Nerve": nerve, "Fascicles": fascicles}
        else:
            morphology_input = {"Nerve": None, "Fascicles": fascicles}

        self.configs[Config.SAMPLE.value]["Morphology"] = morphology_input

        sample_path = os.path.join(self.path(Config.SAMPLE, 'samples_path'),
                                   str(self.search(Config.RUN, 'sample')),
                                   'sample.json')

        TemplateOutput.write(self.configs[Config.SAMPLE.value], sample_path)

        self.morphology = morphology_input
        return self
