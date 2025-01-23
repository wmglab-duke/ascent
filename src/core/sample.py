#!/usr/bin/env python3.7

"""Defines Sample class.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""
import copy
import math
import os
import shutil
import warnings

import cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import binary_fill_holes
from shapely.affinity import affine_transform
from shapely.geometry import MultiPoint, Point
from skimage import morphology

from src.core import Deformable, Fascicle, Map, Nerve, Slide, Trace
from src.utils import (
    Config,
    Configurable,
    ContourMode,
    DeformationMode,
    IncompatibleParametersError,
    MaskError,
    MaskFileNames,
    MaskInputMode,
    NerveMode,
    PerineuriumThicknessMode,
    ReshapeNerveMode,
    Saveable,
    ScaleInputMode,
    SetupMode,
    ShrinkageMode,
    WriteMode,
)


class Sample(Configurable, Saveable):
    """Instantiate Sample, a collection of Slides.

    Required (Config.) JSON's:     SAMPLE     RUN
    """

    def __init__(self):
        """Initialize Sample."""
        # Initializes superclass
        Configurable.__init__(self)

        # Initialize slides
        self.contour_mode = None
        self.scale_input_mode = None
        self.index = None
        self.start_directory = None
        self.nerve = None
        self.sample_rotation = None
        self.deform_ratio = None
        self.deform_mode = None
        self.reshape_nerve_mode = None
        self.nerve_mode = None
        self.mask_input_mode = None
        self.slides: list[Slide] = []
        self._init_slides: list[Slide] = []

        # Set instance variable map
        self.map = None

        # Set instance variable morphology
        self.morphology = {}

        # Add JSON for perineurium thickness relationship with nerve morphology metrics
        # used to calculate contact impedances if "use_ci" is True
        self.add(
            SetupMode.NEW,
            Config.CI_PERINEURIUM_THICKNESS,
            os.path.join('config', 'system', 'ci_peri_thickness.json'),
        )

    @property
    def init_slides(self) -> list[Slide]:
        """Get initial slides list.

        Getter method for initial slides, which have only been converted to micron units, but not further
        tranformed from initial traces computed from input images.

        :return: List of initial slides (converted to microns, no further transforms)
        """
        return self._init_slides

    def init_map(self, map_mode: SetupMode) -> 'Sample':
        """Initialize the map.

        NOTE: the Config.SAMPLE json must have been externally added.

        :raises KeyError: if sample config is not found
        :param map_mode: should be old for now, but keeping as parameter in case needed in the future
        :return: self
        """
        if Config.SAMPLE.value not in self.configs:
            raise KeyError("Missing Config.SAMPLE configuration!")

        # Make a slide map
        self.map = Map()
        self.map.add(SetupMode.OLD, Config.SAMPLE, self.configs[Config.SAMPLE.value])
        self.map.init_post_config(map_mode)

        return self

    def scale(self, factor, center: list[float] = None) -> 'Sample':
        """Scale all slides to the correct unit.

        :param factor: factor by which to scale the image (1=no change)
        :param center: origin [x, y] around which to scale the image
        :return: self
        """
        for slide in self.slides:
            slide.scale(factor, center)

        return self

    def smooth(self, n_distance, i_distance) -> 'Sample':
        """Smooth traces for all slides.

        :param n_distance: distance to inflate and deflate the nerve trace
        :param i_distance: distance to inflate and deflate the fascicle traces
        :return: self
        """
        for slide in self.slides:
            slide.smooth_traces(n_distance, i_distance)

        return self

    def generate_perineurium(self, fit: dict) -> 'Sample':
        """Add perineurium to inners.

        :param fit: dictionary of perineurium fit parameters
        :return: self
        """
        for slide in self.slides:
            slide.generate_perineurium(fit)

        return self

    def im_preprocess(self, path):
        """Perform cleaning operations on the input image, and convert to uint8.

        Important that at the very least image is converted to uint8

        :raises ValueError: if object removal area is negative
        :raises MaskError: if the mask is not binary
        :param path: path to image which will be processed
        """
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if len(np.unique(img)) != 2:
            raise MaskError("Image provided is not binary")

        if self.search(Config.SAMPLE, 'image_preprocessing', 'fill_holes', optional=True) is True:
            if self.search_mode(MaskInputMode, Config.SAMPLE) == MaskInputMode.INNER_AND_OUTER_COMPILED:
                print(
                    'WARNING: Skipping fill holes since MaskInputMode is INNER_AND_OUTER_COMPILED. '
                    'Change fill_holes to False to suppress this warning.'
                )
            else:
                img = binary_fill_holes(img).astype(int)
        removal_size = self.search(Config.SAMPLE, 'image_preprocessing', 'object_removal_area', optional=True)
        if removal_size:
            if removal_size < 0:
                raise ValueError(
                    "Object removal area (image_preprocessing->object_removal_area->sample.json) cannot be negative"
                )
            img = morphology.remove_small_objects(img.astype(bool), removal_size)
        imgout = (255 * (img / np.amax(img))).astype(np.uint8)
        cv2.imwrite(path, imgout)

    @staticmethod
    def get_factor(
        scale_bar_mask_path: str,
        scale_bar_length: float,
        scale_bar_is_literal: bool,
    ) -> 'Sample':
        """Get scaling factor (micrometers per pixel).

        :param scale_bar_mask_path: path to binary mask with white straight (horizontal) scale bar
        :param scale_bar_length: length (in global units as determined by config/user) of the scale bar
        :param scale_bar_is_literal: if True, then scale_bar_length is the factor, otherwise calculate from image
        :raises MaskError: if TIF file is not valid
        :return: scaling factor
        """
        if scale_bar_is_literal:
            # use explicitly specified um/px scale instead of drawing from a scale bar image
            return scale_bar_length

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
            raise MaskError("Invalid TIF file format passed into the program")

        # find the length of the scale bar by finding total range of "max white" indices
        scale_bar_pixels = max(indices) - min(indices) + 1

        # calculate scale factor as unit/pixel
        return scale_bar_length / scale_bar_pixels

    def build_file_structure(self, printing: bool = False) -> 'Sample':
        """Build the file structure for morphology inputs.

        :param printing: bool, gives user console output
        :raises FileNotFoundError: If the input folder does not exist or has no files
        :raises ValueError: If more than one slide provided
        :return: self
        """
        scale_input_mode = self.search_mode(ScaleInputMode, Config.SAMPLE, optional=True)
        # For backwards compatibility, if scale mode is not specified assume a mask image is provided
        if scale_input_mode is None:
            scale_input_mode = ScaleInputMode.MASK

        sample_index = self.search(Config.RUN, 'sample')

        # get starting point so able to go back
        start_directory: str = os.getcwd()

        # get sample NAME
        sample: str = self.search(Config.SAMPLE, 'sample')

        # ADDITION: if only one slide present, check if names abide by <NAME>_0_0_<CODE>.tif format
        #           if not abiding, rename files so that they abide
        if len(self.map.slides) == 1:
            source_dir = os.path.join(*self.map.slides[0].data()[3])
            if not os.path.exists(source_dir) or len(os.listdir(source_dir)) == 0:
                raise FileNotFoundError("Could not find the input defined in the 'sample' field of sample.json.")
            # convert any TIFF to TIF
            [os.rename(x, os.path.splitext(x)[0] + '.tif') for x in os.listdir(source_dir) if x.endswith('.tiff')]
            source_files = os.listdir(source_dir)
            mask_fnames = [f.value for f in MaskFileNames if f.value in source_files]
            for mask_fname in mask_fnames:
                shutil.move(
                    os.path.join(source_dir, mask_fname),
                    os.path.join(source_dir, f'{sample}_0_0_{mask_fname}'),
                )
        else:
            raise ValueError("More than one slide provided")

        # loop through each slide
        for slide_info in self.map.slides:
            # unpack data and force cast to string
            cassette, number, _, source_directory = slide_info.data()
            cassette, number = (str(item) for item in (cassette, number))

            scale_was_copied = False
            for directory_part in 'samples', str(sample_index), 'slides', cassette, number, 'masks':
                os.makedirs(directory_part, exist_ok=True)
                os.chdir(directory_part)
                # only try to copy scale image if it is being used

                if (
                    scale_input_mode == ScaleInputMode.MASK
                    and (directory_part == str(sample_index))
                    and not scale_was_copied
                ):
                    scale_source_file = os.path.join(
                        start_directory,
                        *source_directory,
                        '_'.join(
                            [
                                sample,
                                cassette,
                                number,
                                MaskFileNames.SCALE_BAR.value,
                            ]
                        ),
                    )
                    if os.path.exists(scale_source_file):
                        shutil.copy2(scale_source_file, MaskFileNames.SCALE_BAR.value)
                    else:
                        raise FileNotFoundError(f"scale_source_file {scale_source_file} not found")

                    scale_was_copied = True

            for target_file in [item.value for item in MaskFileNames if item != MaskFileNames.SCALE_BAR]:
                source_file = os.path.join(
                    start_directory, *source_directory, '_'.join([sample, cassette, number, target_file])
                )
                if printing:
                    print(f'source: {source_file}\ntarget: {target_file}')
                if os.path.exists(source_file):
                    if printing:
                        print('\tFOUND\n')
                    shutil.copy2(source_file, target_file)
                else:
                    if printing:
                        print('\tNOT FOUND\n')

            os.chdir(start_directory)

            return self

    def parse_modes(self):
        """Get all modes from sample.json."""
        # get parameters (modes) from configuration file
        self.mask_input_mode = self.search_mode(MaskInputMode, Config.SAMPLE)
        self.nerve_mode = self.search_mode(NerveMode, Config.SAMPLE)
        self.reshape_nerve_mode = self.search_mode(ReshapeNerveMode, Config.SAMPLE)
        self.deform_mode = self.search_mode(DeformationMode, Config.SAMPLE)
        self.scale_input_mode = self.search_mode(ScaleInputMode, Config.SAMPLE, optional=True)
        self.sample_rotation = self.search(Config.SAMPLE, "rotation", optional=True)
        self.contour_mode = self.search_mode(ContourMode, Config.SAMPLE, optional=True)

        # For backwards compatibility, if scale mode is not specified assume a mask image is provided
        if self.scale_input_mode is None:
            self.scale_input_mode = ScaleInputMode.MASK
        if self.contour_mode is None:
            self.contour_mode = ContourMode.SIMPLE

    @staticmethod
    def mask_exists(mask_file_name: MaskFileNames):
        """Check if a mask exists (.tif file).

        :param mask_file_name: MaskFileNames, name of mask file
        :return: bool, True if mask exists
        """
        return os.path.exists(mask_file_name.value)

    def calculate_orientation(self, slide):
        """Calculate orientation angle from a.tif.

        :param slide: Slide object
        :raises MaskError: If the mask has an invalid number of objects
        :return: Slide object
        """
        img = np.flipud(cv2.imread(MaskFileNames.ORIENTATION.value, -1))

        if len(img.shape) > 2 and img.shape[2] > 1:
            img = img[:, :, 0]

        contour, _ = cv2.findContours(img, cv2.RETR_TREE, self.contour_mode.value)
        if len(contour) > 1:
            raise MaskError(
                "Multiple objects were found in orientation mask. A single object of white pixels must be provided"
            )
        if len(contour) < 1:
            raise MaskError("No objects were found in orientation mask. An object of white pixels must be provided")
        trace = Trace(
            [point + [0] for point in contour[0][:, 0, :]],
        )

        # choose outer (based on if nerve is present)
        outer = slide.nerve if (slide.nerve is not None) else slide.fascicles[0].outer

        # create line between outer centroid and orientation centroid
        orientation_centroid = trace.centroid()
        outer_x, outer_y = outer.centroid()
        ori_x, ori_y = orientation_centroid

        # set orientation_angle
        slide.orientation_angle = np.arctan2(ori_y - outer_y, ori_x - outer_x)

        return slide

    def mask_validation(self):
        """Validate mask file dimensions.

        :raises MaskError: If mask dimensions are not equal
        :raises FileNotFoundError: If mask file is not found
        """
        mask_dims = []
        for mask in ["COMPILED", "INNERS", "OUTERS", "NERVE", "ORIENTATION"]:
            maskfile = getattr(MaskFileNames, mask)
            if self.mask_exists(maskfile):
                mask_dims.append(cv2.imread(maskfile.value).shape)
                self.im_preprocess(maskfile.value)
        if len(mask_dims) == 0:
            raise FileNotFoundError("No input morphology masks found")
        if not np.all(np.array(mask_dims) == mask_dims[0]):
            raise MaskError("Input morphology masks do not have identical dimensions")
        scalemask = MaskFileNames.SCALE_BAR
        if self.mask_exists(scalemask):
            mask_dims.append(cv2.imread(scalemask.value).shape)
            if not np.all(np.array(mask_dims) == mask_dims[0]):
                print(
                    'WARNING: Scale bar mask has a different resolution than morphology masks. \n'
                    'Program will continue and assume that the scale bar mask microns/pixel ratio is correct.'
                )

    def get_fascicles_from_masks(self, mask_input_mode):
        """Generate fascicle traces from input masks.

        :param mask_input_mode: MaskInputMode
        :raises FileNotFoundError: if a mask file is not found
        :raises ValueError: if mask input mode is not recognized
        :return: list of fascicles
        """
        # assign fascicle mask files
        if mask_input_mode not in MaskInputMode:
            raise ValueError("Invalid MaskInputMode in Sample.")

        if mask_input_mode == MaskInputMode.INNER_AND_OUTER_COMPILED:
            if self.mask_exists(MaskFileNames.COMPILED):
                # first generate outer and inner images
                inner_mask = os.path.split(MaskFileNames.COMPILED.value)[0] + 'i_from_c.tif'
                outer_mask = os.path.split(MaskFileNames.COMPILED.value)[0] + 'o_from_c.tif'
                self.io_from_compiled(MaskFileNames.COMPILED.value, inner_mask, outer_mask)

            else:
                raise FileNotFoundError("Compiled masks required for input mode INNER_AND_OUTER_COMPILED.")
        else:
            if not self.mask_exists(MaskFileNames.INNERS):
                raise FileNotFoundError("Inner mask required for input mode INNERS.")
            inner_mask = MaskFileNames.INNERS.value
            if mask_input_mode == MaskInputMode.INNER_AND_OUTER_SEPARATE:
                if not self.mask_exists(MaskFileNames.OUTERS):
                    raise FileNotFoundError("Inner AND outer masks required for input mode INNER_AND_OUTER_SEPARATE.")
                outer_mask = MaskFileNames.OUTERS.value
            else:  # INNERS mode
                outer_mask = None

        # generate fascicle objects from masks
        return Fascicle.to_list(inner_mask, outer_mask, self.contour_mode)

    def get_epineurium_from_mask(self):
        """Generate epineurium trace from mask.

        :raises FileNotFoundError: if epineurium mask is not found
        :return: Nerve object
        """
        if not self.mask_exists(MaskFileNames.NERVE):
            raise FileNotFoundError("NerveMode is PRESENT, but no nerve mask was found.")
        img_nerve = cv2.imread(MaskFileNames.NERVE.value, -1)

        if len(img_nerve.shape) > 2 and img_nerve.shape[2] > 1:
            img_nerve = img_nerve[:, :, 0]

        contour, _ = cv2.findContours(np.flipud(img_nerve), cv2.RETR_TREE, self.contour_mode.value)
        return Nerve(
            Trace(
                [point + [0] for point in contour[0][:, 0, :]],
            )
        )

    def generate_slide(self, slide_info):
        """Create slide from input masks.

        :param slide_info: SlideInfo
        :raises IncompatibleParametersError: If multiple fascicles are present and NerveMode is not set to PRESENT
        :return: Slide object
        """
        # unpack data and force cast to string
        cassette, number, position, _ = slide_info.data()
        cassette, number = (str(item) for item in (cassette, number))

        os.chdir(os.path.join('samples', str(self.index), 'slides', cassette, number, 'masks'))

        # convert any TIFF to TIF
        [os.rename(x, os.path.splitext(x)[0] + '.tif') for x in os.listdir('.')]

        # preprocess binary masks
        self.mask_validation()
        # get fascicle objects
        fascicles = self.get_fascicles_from_masks(self.mask_input_mode)

        # get nerve object if present
        if self.nerve_mode == NerveMode.PRESENT:
            nerve = self.get_epineurium_from_mask()
        else:
            if len(fascicles) > 1:
                raise IncompatibleParametersError(
                    "NerveMode is not set to present (Sample.json). "
                    "Multifascicular simulations without a nerve mask are not supported"
                )
            nerve = None

        slide: Slide = Slide(
            fascicles,
            nerve,
            self.nerve_mode,
            will_reposition=(self.deform_mode != DeformationMode.NONE),
        )

        slide.validate()

        # get orientation angle (used later to calculate pos_ang for model.json)
        if self.mask_exists(MaskFileNames.ORIENTATION):
            slide = self.calculate_orientation(slide)

        os.chdir(self.start_directory)

        return slide  # noqa: R504

    def correct_shrinkage(self, slide):
        """Apply shrinkage correction to slide.

        :param slide: Slide
        :raises ValueError: if shrinkage mode is invalid
        :raises ValueError: if shrinkage correction would result in further shrinkage
        """
        # shrinkage correction
        s_mode = self.search_mode(ShrinkageMode, Config.SAMPLE, optional=True)
        s_pre = self.search(Config.SAMPLE, "scale", "shrinkage")
        if s_mode is None:
            print(
                'WARNING: ShrinkageMode in Config.Sample is not defined or mode provided is not a known option. '
                'Proceeding with backwards compatible (i.e., original default functionality) of LENGTH_FORWARDS'
                ' shrinkage correction.\n'
            )
            shrinkage_correction = 1 + s_pre
        else:
            if s_mode == ShrinkageMode.LENGTH_BACKWARDS:
                shrinkage_correction = 1 / (1 - s_pre)
            elif s_mode == ShrinkageMode.LENGTH_FORWARDS:
                shrinkage_correction = s_pre + 1
            elif s_mode == ShrinkageMode.AREA_BACKWARDS:
                shrinkage_correction = 1 / np.sqrt(1 - s_pre)
            elif s_mode == ShrinkageMode.AREA_FORWARDS:
                shrinkage_correction = np.sqrt(1 + s_pre)
            else:
                raise ValueError("Invalid ShrinkageMode defined in sample.json")

        if shrinkage_correction < 1:
            raise ValueError(
                "Shrinkage parameter (s) derived from your input (Sample->shrinkage->scale) "
                "results in further shrinkage, rather than expansion, which is not expected functionality."
            )

        slide.scale(shrinkage_correction)

    def apply_scaling(self):
        """Scales from pixels to microns.

        :raises FileNotFoundError: if scale image is required and not found
        :raises ValueError: if scale input mode is not valid
        """
        # create scale bar path
        if self.scale_input_mode == ScaleInputMode.MASK:
            scale_path = os.path.join('samples', str(self.index), MaskFileNames.SCALE_BAR.value)
        elif self.scale_input_mode == ScaleInputMode.RATIO:
            scale_path = ''
        else:
            raise ValueError("Invalid scale input mode")

        # get scaling factor (to convert from pixels to microns)
        if os.path.exists(scale_path) and self.scale_input_mode == ScaleInputMode.MASK:
            factor = self.get_factor(
                scale_path,
                self.search(Config.SAMPLE, 'scale', 'scale_bar_length'),
                False,
            )
        elif self.scale_input_mode == ScaleInputMode.RATIO:
            factor = self.get_factor(scale_path, self.search(Config.SAMPLE, 'scale', 'scale_ratio'), True)
        else:
            print(scale_path)
            raise FileNotFoundError("Scale bar for nerve micrograph does not exist.")

        # scale to microns
        self.scale(factor, [0.0, 0.0])

    def apply_smoothing(self):
        """Smooth traces.

        :raises IncompatibleParametersError: if nerve distance is not defined for NERVE_MODE = PRESENT
        """
        # get smoothing params
        n_distance = self.search(Config.SAMPLE, 'smoothing', 'nerve_distance', optional=True)
        i_distance = self.search(Config.SAMPLE, 'smoothing', 'fascicle_distance', optional=True)
        # smooth traces
        if not (n_distance == i_distance is None):
            if self.nerve_mode == NerveMode.PRESENT and n_distance is None:
                raise IncompatibleParametersError(
                    "If NerveMode is set to PRESENT and smoothing is defined in Sample.json, "
                    "nerve_distance must be defined"
                )
            self.smooth(n_distance, i_distance)

    def prepare_perineurium(self):
        """Generate perineurium."""
        peri_thick_mode: PerineuriumThicknessMode = self.search_mode(PerineuriumThicknessMode, Config.SAMPLE)

        perineurium_thk_info: dict = self.search(
            Config.CI_PERINEURIUM_THICKNESS,
            PerineuriumThicknessMode.parameters.value,
            str(peri_thick_mode).split('.')[-1],
        )

        self.generate_perineurium(perineurium_thk_info)

    def deform_slide(self, slide):
        """Deform a slide based on user parameters.

        :param slide: Slide object
        :raises KeyError: if deform_ratio is not defined in Config.Sample
        :raises ValueError: if deform mode is invalid
        :return: Slide object
        """
        if self.deform_mode != DeformationMode.PHYSICS:
            raise ValueError("Invalid DeformationMode in Sample.")
        if 'morph_count' in self.search(Config.SAMPLE):
            morph_count = self.search(Config.SAMPLE, 'morph_count')
        else:
            morph_count = 100

        if 'deform_ratio' in self.search(Config.SAMPLE):
            deform_ratio = self.search(Config.SAMPLE, 'deform_ratio')
            print(f'\tdeform ratio set to {deform_ratio}')
        else:
            raise KeyError("Deformation mode is set to physics, but no deform ratio is defined in sample.json")

        sep_fascicles = self.search(Config.SAMPLE, "boundary_separation", "fascicles")

        print(f'\tensuring minimum fascicle-fascicle separation of {sep_fascicles} um')

        if 'nerve' in self.search(Config.SAMPLE, 'boundary_separation'):
            sep_nerve = self.search(Config.SAMPLE, 'boundary_separation', 'nerve')
            print(f'\tensuring minimum nerve-fascicle separation of {sep_nerve} um')
            sep_nerve = sep_nerve - sep_fascicles / 2
        else:
            sep_nerve = None

        # scale nerve trace down by sep nerve, will be scaled back up later
        pre_area = slide.nerve.area()
        slide.nerve.offset(distance=-sep_nerve)
        slide.nerve.scale(1)
        slide.nerve.points = np.flip(slide.nerve.points, axis=0)

        if (
            self.configs[Config.CLI_ARGS.value].get('render_deform') is True
            or self.search(Config.SAMPLE, 'render_deform', optional=True) is True
        ):
            render_deform = True
            print('Sample deformation is set to render. Rendering...')
        else:
            render_deform = False

        deformable = Deformable.from_slide(copy.deepcopy(slide), ReshapeNerveMode.CIRCLE)

        movements, rotations = deformable.deform(
            morph_count=morph_count,
            render=render_deform,
            minimum_distance=sep_fascicles,
            ratio=deform_ratio,
        )

        partially_deformed_nerve = Deformable.deform_steps(deformable.start, deformable.end, morph_count, deform_ratio)[
            -1
        ]

        for move, angle, fascicle in zip(movements, rotations, slide.fascicles):
            fascicle.shift(list(move) + [0])
            fascicle.rotate(angle)

        if deform_ratio != 1 and partially_deformed_nerve is not None:
            partially_deformed_nerve.shift(-np.asarray(list(partially_deformed_nerve.centroid()) + [0]))
            slide.nerve = partially_deformed_nerve
            slide.nerve.offset(distance=sep_nerve)
        else:
            slide.nerve = slide.reshaped_nerve(self.reshape_nerve_mode)
        # deforms+offsets usually shrinks the area a bit, so reset back to the original area
        if slide.nerve.area() != pre_area:
            slide.nerve.scale((pre_area / slide.nerve.area()) ** 0.5)
        else:
            print(f'Note: nerve area before deformation was {pre_area}, post deformation is {self.nerve.area()}')

        # shift slide about (0,0)
        slide.move_center(np.array([0, 0]))
        return slide

    def populate(self) -> 'Sample':
        """Populate a sample with trace objects using input images.

        :raises IncompatibleParametersError: If the sample.json file is not configured correctly.
        :return: Sample object
        """

        def populate_plotter(slide, title: str, filename: str):
            plt.figure()
            if (slide.bounds()[2] - slide.bounds()[0]) > 1000:
                scalebar_length = 1
                scalebar_units = 'mm'
            else:
                scalebar_length = 100
                scalebar_units = 'μm'
            slide.plot(
                final=False,
                fix_aspect_ratio='True',
                axlabel="\u03bcm",
                title=title,
                scalebar=True,
                scalebar_length=scalebar_length,
                scalebar_units=scalebar_units,
            )
            plt.savefig(plotpath + '/' + filename, dpi=400)
            if self.search(Config.RUN, "popup_plots", optional=True) is True:
                plt.show()
            else:
                plt.clf()
                plt.close('all')

        # get all modes
        self.parse_modes()

        # get starting point so able to go back
        self.start_directory: str = os.getcwd()

        # get sample name
        self.index: int = self.search(Config.RUN, 'sample')

        # generate plotpath if not existing
        plotpath = os.path.join('samples', str(self.index), 'plots')
        os.makedirs(plotpath, exist_ok=True)

        # Generate slides
        for slide_info in self.map.slides:
            self.slides.append(self.generate_slide(slide_info))

        # scale to microns
        self.apply_scaling()

        # plot initial scaled sample
        populate_plotter(self.slides[0], 'Initial sample from morphology masks', 'sample_initial')

        # Save untransformed slides without shrinkage correction or rotation (defined in microns)
        self._init_slides = copy.deepcopy(self.slides)
        for slide in self._init_slides:
            slide.scale(1.0)  # connect trace for closed geometry

        # Reset the affine transformation matrices to track only the steps after micron scaling
        # (deformation, shrinkage correction)
        self.__reset_transform()

        # apply shrinkage correction
        for i in range(len(self.slides)):
            self.correct_shrinkage(self.slides[i])

        # apply smoothing
        self.apply_smoothing()

        # after scaling, if only inners were provided, generate outers
        if self.mask_input_mode == MaskInputMode.INNERS:
            self.prepare_perineurium()

        if self.deform_mode == DeformationMode.NONE:
            sep_nerve = self.search(Config.SAMPLE, 'boundary_separation').get('nerve')
            if sep_nerve != 0:
                warnings.warn(
                    f'NO DEFORMATION is happening! AND sep_nerve is not 0, sep_nerve = {sep_nerve}', stacklevel=2
                )
        else:
            if self.nerve_mode == NerveMode.NOT_PRESENT:
                raise IncompatibleParametersError("Cannot reposition without NerveMode.PRESENT")
            # repositioning!
            for slide in self.slides:
                self.deform_slide(slide)
        for slide in self.slides:
            # shift slide about (0,0)
            slide.move_center(np.array([0, 0]))

            # Rotate sample
            if self.sample_rotation is not None:
                if slide.orientation_angle is not None:
                    raise IncompatibleParametersError(
                        "Rotation cannot be defined in sample.json if using an orientation image input."
                    )
                slide.rotate(math.radians(self.sample_rotation))

        # scale with ratio = 1 (no scaling happens, but connects the ends of each trace to itself)
        self.scale(1)

        # ensure that nothing went wrong in slide processing
        self.slides[0].validate(plotpath=plotpath)

        populate_plotter(self.slides[0], 'Final sample after any user specified processing', 'sample_final')

        affine_slides = self.init_transform()
        populate_plotter(affine_slides[0], 'Sample after any user specified affine only processing', 'sample_affine')

        return self

    @staticmethod
    def io_from_compiled(imgin, i_out, o_out):
        """Generate inner and outer mask from compiled mask.

        :param imgin: path to input image (hint: c.tif)
        :param i_out: full path to desired output inner mask
        :param o_out: full path to desired output outer mask
        """
        compiled = cv2.imread(imgin, -1)

        imgnew = cv2.bitwise_not(compiled)

        h, w = imgnew.shape[:2]

        mask = np.zeros((h + 2, w + 2), np.uint8)

        cv2.floodFill(imgnew, mask, (0, 0), 0)

        cv2.imwrite(i_out, imgnew)

        cv2.imwrite(o_out, compiled + imgnew)

    def write(self, mode: WriteMode) -> 'Sample':
        """Write entire list of slides.

        :param mode: WriteMode
        :raises NotImplementedError: if mode is not implemented
        :raises OSError: if that path to write to does not exist
        :return: self
        """
        # get starting point so able to go back
        start_directory: str = os.getcwd()

        # get path to sample slides
        sample_path = os.path.join('samples', str(self.search(Config.RUN, 'sample')), 'slides')

        # loop through the slide info (index i SHOULD correspond to slide in self.slides)
        for i, slide_info in enumerate(self.map.slides):
            # unpack data and force cast to string
            cassette, number, _, source_directory = slide_info.data()
            cassette, number = (str(item) for item in (cassette, number))

            # build path to slide and ensure that it exists before proceeding
            slide_path = os.path.join(sample_path, cassette, number)
            if not os.path.exists(slide_path):
                raise OSError("Path to slide must have already been created.")

            # change directories to slide path
            os.chdir(slide_path)

            # build the directory for output (name is the write mode)
            if mode == WriteMode.SECTIONWISE2D:
                directory_to_create = 'sectionwise2d'
            elif mode == WriteMode.SECTIONWISE:
                directory_to_create = 'sectionwise'
            else:
                raise NotImplementedError("Unimplemented write mode.")

            # clear directory if it exists, then create
            if os.path.exists(directory_to_create):
                shutil.rmtree(directory_to_create, ignore_errors=True)
            os.makedirs(directory_to_create, exist_ok=True)

            os.chdir(directory_to_create)

            # WRITE
            self.slides[i].write(mode, os.getcwd())

            # go back up to start directory, then to top of loop
            os.chdir(start_directory)

        return self

    def output_morphology_data(self) -> 'Sample':
        """Output morhodology data for the sample to sample.json.

        :return: self
        """
        nerve_mode = self.search_mode(NerveMode, Config.SAMPLE)

        fascicles = [fascicle.morphology_data() for fascicle in self.slides[0].fascicles]

        if nerve_mode == NerveMode.PRESENT:
            nerve = Nerve.morphology_data(self.slides[0].nerve)
            morphology_input = {"Nerve": nerve, "Fascicles": fascicles}
        else:
            morphology_input = {"Nerve": None, "Fascicles": fascicles}

        self.configs[Config.SAMPLE.value]["Morphology"] = morphology_input

        sample_path = os.path.join('samples', str(self.search(Config.RUN, 'sample')), 'sample.json')

        Configurable.write(self.configs[Config.SAMPLE.value], sample_path)

        self.morphology = morphology_input
        return self

    def init_transform(self) -> list[Slide]:
        """Transform initial slides based on the affine transformation trackers in each trace.

        Additional non-affine operations (e.g. Trace.smooth and Trace.offset) can be applied depending on configuration
        to yield the final sample morphology. This function yields the sample transformations with only affine
        transformations (translation, scaling, rotation).

        :return: List of slides with affine transformed applied.
        """
        # Iterate over final slides (which have transformation trackers) and initial slides (untransformed).
        tfm_slides = copy.deepcopy(self._init_slides)
        for slide, init_slide in zip(self.slides, tfm_slides):
            # Skip nerve transformation if there is no nerve (epineurium) morphology
            if self.nerve_mode == NerveMode.PRESENT:
                init_slide.nerve.transform(slide.nerve.transform_matrix)
            for fasc, init_fasc in zip(slide.fascicles, init_slide.fascicles):
                if self.mask_input_mode == MaskInputMode.INNERS and len(fasc.inners) > 0:
                    # If only inners were initially provided, the untransformed outer corresponds to the final inner.
                    init_fasc.outer.transform(fasc.inners[0].transform_matrix)
                else:
                    # Otherwise outers and inners map 1-to-1 between transformed and untransformed slide traces.
                    init_fasc.outer.transform(fasc.outer.transform_matrix)
                    for inner, init_inner in zip(fasc.inners, init_fasc.inners):
                        init_inner.transform(inner.transform_matrix)
        return tfm_slides

    def point_transform(self, points: np.ndarray, by_slide=False) -> np.array:
        """Transform points from original coordinates to final.

        Transforms points from the original coordinate system to final morphology based on affine transforms tracked
        in each trace. If the point falls within a trace, it's transformed according to that Trace's transform_matrix.

        :param points: list of points with the last two dimensions corresponding to # of points and x, y, [z]
        :param by_slide: if True, the first dimension of points corresponds to each slide in Sample.slides.
        :return: Transformed list of points with same shape as input.
        """

        def shapely_point_transform(pts, transform_mat, return_ndim=3):
            m_pts = MultiPoint(pts)
            shapely_mat = Trace.get_shapely_affine(transform_mat, return_ndim)
            m_pts = affine_transform(m_pts, shapely_mat)
            if return_ndim == 2:
                return np.asarray([(g.x, g.y) for g in m_pts.geoms])

            return np.asarray([(g.x, g.y, g.z) for g in m_pts.geoms])

        np_points = np.asarray(points)

        if by_slide:
            assert len(np_points) == len(
                self.slides
            ), "When using by_slide, first axis must match number of Sample slides"
        else:
            np_points = np.asarray([np_points for _ in self.slides])

        assert len(np_points.shape) > 2, "Input must have last two axes corresponding to n_points and n_coordinates"

        mat_ndim = 3
        if np_points.shape[-1] == 2:
            mat_ndim = 2
        assert np_points.shape[-1] in [
            2,
            3,
        ], "Points must have a last axis of length 2 or 3 corresponding to [x, y] or [x, y, z], respectively"

        tfm_points = []
        for s_points, slide, init_slide in zip(np_points, self.slides, self._init_slides):
            flat_points = np.reshape(s_points, (-1, s_points.shape[-1]))

            fibs_in_fasc = np.zeros(flat_points.shape[0])
            out_to_fib, _ = init_slide.map_points(flat_points)
            for fasc_idx, otf in enumerate(out_to_fib):
                for inner_idx, fiber_inds in enumerate(otf):
                    if len(fiber_inds) == 0:
                        # No fibers in this inner
                        continue
                    if len(slide.fascicles[fasc_idx].inners) == 0:
                        # This shouldn't happen
                        warnings.warn('Transforming with no inners', stacklevel=2)
                        flat_points[fiber_inds, :] = shapely_point_transform(
                            flat_points[fiber_inds, :],
                            slide.fascicles[fasc_idx].outer.transform_matrix,
                            return_ndim=mat_ndim,
                        )
                    else:
                        flat_points[fiber_inds, :] = shapely_point_transform(
                            flat_points[fiber_inds, :],
                            slide.fascicles[fasc_idx].inners[inner_idx].transform_matrix,
                            return_ndim=mat_ndim,
                        )
                    fibs_in_fasc[fiber_inds] = 1

            if self.nerve_mode == NerveMode.PRESENT:
                n_nerve_pts = 0
                for f_idx in np.flatnonzero(fibs_in_fasc == 0):
                    if Point(flat_points[f_idx]).within(init_slide.nerve.polygon()):
                        fibs_in_fasc[f_idx] = -1
                        n_nerve_pts += 1

                if n_nerve_pts > 0:
                    flat_points[fibs_in_fasc == -1, :] = shapely_point_transform(
                        flat_points[fibs_in_fasc == -1, :], slide.nerve.transform_matrix, return_ndim=mat_ndim
                    )

            tfm_points.append(flat_points.reshape(s_points.shape).tolist())

        return np.asarray(tfm_points)

    def __reset_transform(self):
        """Reset the transform matrix for each Trace in Sample."""
        for slide in self.slides:
            if slide.nerve is not None:
                slide.nerve.reset_transform()
            for fascicle in slide.fascicles:
                fascicle.reset_transform()
