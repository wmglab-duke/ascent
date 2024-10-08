"""Defines Model class.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""

import os
import warnings
from copy import deepcopy

import numpy as np
from quantiphy import Quantity
from shapely.geometry import Point

from src.core import Sample, Slide, Waveform
from src.utils import (
    Config,
    Configurable,
    CuffShiftMode,
    IncompatibleParametersError,
    MorphologyError,
    NerveMode,
    PerineuriumResistivityMode,
    ReshapeNerveMode,
    Saveable,
    SetupMode,
)


class Model(Configurable, Saveable):
    """Controls parameters associated with a model."""

    def __init__(self):
        """Initialize Model."""
        # Initializes superclass
        Configurable.__init__(self)

    def compute_cuff_shift(self, sample: Sample, sample_config: dict):
        """Compute the Cuff Shift for single or multiple cuffs in a given model.

        :param sample: Sample, sample object
        :param sample_config: dict, sample config
        :raises ValueError: if deform_ratio is not between 0 and 1 (inclusive)
        :return: self
        """
        # NOTE: ASSUMES SINGLE SLIDE
        # add temporary model configuration
        self.add(SetupMode.OLD, Config.SAMPLE, sample_config)

        # fetch slide
        slide = sample.slides[0]

        # fetch nerve mode
        nerve_mode: NerveMode = self.search_mode(NerveMode, Config.SAMPLE)

        if nerve_mode == NerveMode.PRESENT:
            if 'deform_ratio' not in self.configs[Config.SAMPLE.value]:
                deform_ratio = 1
            else:
                deform_ratio = self.search(Config.SAMPLE, 'deform_ratio')
            if deform_ratio < 0 or deform_ratio > 1:
                raise ValueError("Deform ratio (sample.json) must be between 0 and 1 (inclusive).")
        else:
            deform_ratio = None

        cuff_data = self.search(Config.MODEL, "cuff")

        if isinstance(
            cuff_data, dict
        ):  # When single cuff configuration is provided, re-adjust data type to allow following for-loop
            if not self.search(Config.MODEL, "cuff", "index", optional=True):  # If not cuff index is provided
                warnings.warn('No "cuff" -> "index" provided in model.json. Assigning cuff index to 0.', stacklevel=2)
                cuff_data["index"] = 0

            cuff_data = [cuff_data]

        cuff_dicts = []

        for cuff_dict in cuff_data:
            cuff_dict = self.cuff_shift_calc(cuff_dict, slide, deform_ratio, nerve_mode, sample_config)
            cuff_dicts.append(cuff_dict)

        self.configs[Config.MODEL.value]['cuff'] = cuff_dicts

        return self

    def cuff_shift_calc(
        self, cuff_dict: dict, slide: Slide, deform_ratio: float, nerve_mode: NerveMode, sample_config: dict
    ):
        """Compute the cuff shift for a single cuff.

        :param cuff_dict: dictionary for single cuff
        :param slide: the sample's slide
        :param deform_ratio: deformation ratio
        :param nerve_mode: whether the nerve is present. Flag from sample config file.
        :param sample_config: sample configuration variables
        :raises ValueError: if deform_ratio is not between 0 and 1 (inclusive)
        :return: updated cuff dictionary
        """
        # get center and radius of nerve's min_bound circle
        nerve_copy = deepcopy(slide.nerve if nerve_mode == NerveMode.PRESENT else slide.fascicles[0].outer)

        # fetch cuff config
        cuff_config: dict = self.load(os.path.join(os.getcwd(), "config", "system", "cuffs", cuff_dict['preset']))

        (
            cuff_code,
            cuff_r_buffer,
            expandable,
            offset,
            r_bound,
            r_f,
            theta_c,
            theta_i,
            x,
            y,
        ) = self.get_cuff_shift_parameters(cuff_config, deform_ratio, nerve_copy, sample_config, slide)

        r_i, theta_f = self.check_cuff_expansion_radius(cuff_code, cuff_config, expandable, r_f, theta_i)

        cuff_shift_mode: CuffShiftMode = self.search_mode(CuffShiftMode, Config.MODEL)

        if cuff_shift_mode not in CuffShiftMode:
            raise ValueError("Invalid CuffShiftMode in Model.")

        # remove (pop) temporary model configuration
        self.configs[Config.MODEL.value]['min_radius_enclosing_circle'] = r_bound
        if slide.orientation_angle is not None:
            theta_c = slide.orientation_angle * (360 / (2 * np.pi)) % 360  # overwrite theta_c, use our own orientation

        # check if a naive mode was chosen
        naive = cuff_shift_mode in [
            CuffShiftMode.NAIVE_ROTATION_MIN_CIRCLE_BOUNDARY,
            CuffShiftMode.NAIVE_ROTATION_TRACE_BOUNDARY,
        ]

        # initialize as 0, only replace values as needed, must be initialized here in case cuff shift mode is NONE
        x_shift = y_shift = 0
        # set pos_ang
        if naive or cuff_shift_mode == CuffShiftMode.NONE:
            cuff_dict['rotate']['pos_ang'] = 0
            if slide.orientation_point is not None:
                print(
                    'Warning: orientation tif image will be ignored because a NAIVE or NONE cuff shift mode was chosen.'
                )
        else:
            cuff_dict['rotate']['pos_ang'] = theta_c - theta_f

        # min circle x and y shift
        if cuff_shift_mode in [
            CuffShiftMode.NAIVE_ROTATION_MIN_CIRCLE_BOUNDARY,
            CuffShiftMode.AUTO_ROTATION_MIN_CIRCLE_BOUNDARY,
        ]:
            if r_i > r_f:
                x_shift = x - (r_i - offset - cuff_r_buffer - r_bound) * np.cos(theta_c * ((2 * np.pi) / 360))
                y_shift = y - (r_i - offset - cuff_r_buffer - r_bound) * np.sin(theta_c * ((2 * np.pi) / 360))

            elif slide.nerve is None or deform_ratio != 1:
                x_shift, y_shift = x, y

        # min trace modes
        elif cuff_shift_mode in [
            CuffShiftMode.NAIVE_ROTATION_TRACE_BOUNDARY,
            CuffShiftMode.AUTO_ROTATION_TRACE_BOUNDARY,
        ]:
            if r_i < r_f:
                x_shift, y_shift = x, y

            else:
                id_boundary = Point(0, 0).buffer(r_i - offset)
                n_boundary = Point(x, y).buffer(r_f)

                if id_boundary.boundary.distance(n_boundary.boundary) < cuff_r_buffer:
                    nerve_copy.shift([x, y, 0])
                    print(
                        "WARNING: NERVE CENTERED ABOUT MIN CIRCLE CENTER (BEFORE PLACEMENT) BECAUSE "
                        "CENTROID PLACEMENT VIOLATED REQUIRED CUFF BUFFER DISTANCE\n"
                    )

                center_x = 0
                center_y = 0
                step = 1  # [um] STEP SIZE
                x_step = step * np.cos(-theta_c + np.pi)  # STEP VECTOR X-COMPONENT
                y_step = step * np.sin(-theta_c + np.pi)  # STEP VECTOR X-COMPONENT

                # shift nerve within cuff until one step within the minimum separation from cuff
                while nerve_copy.polygon().boundary.distance(id_boundary.boundary) >= cuff_r_buffer:
                    nerve_copy.shift([x_step, y_step, 0])
                    center_x -= x_step
                    center_y -= y_step

                # to maintain minimum separation from cuff, reverse last step
                center_x += x_step
                center_y += y_step

                x_shift, y_shift = center_x, center_y

        cuff_dict['shift']['x'] = x_shift
        cuff_dict['shift']['y'] = y_shift
        return cuff_dict

    def get_cuff_shift_parameters(self, cuff_config, deform_ratio, nerve_copy, sample_config, slide):
        """Calculate parameters for cuff shift.

        :param cuff_config: cuff configuration
        :param deform_ratio: deform ratio
        :param nerve_copy: copied nerve object
        :param sample_config: sample configuration
        :param slide: slide object to shift cuff around
        :raises MorphologyError: if slide is not centered at origin
        :return: (cuff code, cuff r buffer, expandable, offset, r_bound, r_f, theta_c, theta_i, x, y)
        """
        # fetch 1-2 letter code for cuff (ex: 'CT')
        cuff_code: str = cuff_config['code']
        # fetch radius buffer string (ex: '0.003 [in]')
        cuff_r_buffer_str: str = [
            item["expression"]
            for item in cuff_config["params"]
            if item["name"] == '_'.join(['thk_medium_gap_internal', cuff_code])
        ][0]
        # calculate value of radius buffer in micrometers (ex: 76.2)
        cuff_r_buffer: float = Quantity(
            Quantity(
                cuff_r_buffer_str.translate(cuff_r_buffer_str.maketrans('', '', ' []')),
                scale='m',
            ),
            scale='um',
        ).real  # [um] (scaled from any arbitrary length unit)
        # Get the boundary and center information for computing cuff shift
        if self.search_mode(ReshapeNerveMode, Config.SAMPLE) and not slide.monofasc() and deform_ratio == 1:
            x, y = 0, 0
            r_bound = np.sqrt(sample_config['Morphology']['Nerve']['area'] / np.pi)
        else:
            x, y, r_bound = nerve_copy.make_circle()
        # next calculate the angle of the "centroid" to the center of min bound circle
        # if mono fasc, just use 0, 0 as centroid (i.e., centroid of nerve same as centroid of all fasc)
        # if poly fasc, use centroid of all fascicle as reference, not 0, 0
        # angle of centroid of nerve to center of minimum bounding circle
        reference_x = reference_y = 0.0
        if not slide.monofasc() and not (round(slide.nerve.centroid()[0]) == round(slide.nerve.centroid()[1]) == 0):
            raise MorphologyError(
                "Slide is not centered at [0,0]"
            )  # if the slide has nerve and is not centered at the nerve throw error
        if not slide.monofasc():
            reference_x, reference_y = slide.fascicle_centroid()
        theta_c = (np.arctan2(reference_y - y, reference_x - x) * (360 / (2 * np.pi))) % 360
        # calculate final necessary radius by adding buffer
        r_f = r_bound + cuff_r_buffer
        # fetch initial cuff rotation (convert to rads)
        theta_i = cuff_config.get('angle_to_contacts_deg') % 360
        # fetch boolean for cuff expandability
        expandable: bool = cuff_config['expandable']
        offset = 0
        for key, coef in cuff_config["offset"].items():
            value_str = [item["expression"] for item in cuff_config["params"] if item['name'] == key][0]
            value: float = Quantity(
                Quantity(value_str.translate(value_str.maketrans('', '', ' []')), scale='m'),
                scale='um',
            ).real  # [um] (scaled from any arbitrary length unit)
            offset += coef * value
        return cuff_code, cuff_r_buffer, expandable, offset, r_bound, r_f, theta_c, theta_i, x, y

    def check_cuff_expansion_radius(self, cuff_code, cuff_config, expandable, r_f, theta_i):
        """Check the cuff expansion radius.

        :param cuff_code: str, cuff code
        :param cuff_config: dict, cuff config
        :param expandable: bool, cuff expandable
        :param r_f: float, final radius
        :param theta_i: float, initial angle of cuff pre expansion
        :raises KeyError: If cuff is expandable and no fixed point is specified
        :raises IncompatibleParametersError: If the cuff is too small for the nerve
        :return: r_i: float, cuff radius pre expansion; theta_f: float, cuff wrap angle used in FEM
        """
        # check radius if not expandable
        if not expandable:
            r_i_str: str = [
                item["expression"] for item in cuff_config["params"] if item["name"] == '_'.join(['R_in', cuff_code])
            ][0]
            r_i: float = Quantity(
                Quantity(r_i_str.translate(r_i_str.maketrans('', '', ' []')), scale='m'),
                scale='um',
            ).real  # [um] (scaled from any arbitrary length unit)

            if not r_f <= r_i:
                raise IncompatibleParametersError("cuff chosen is too small for nerve sample provided")

            theta_f = theta_i
        else:
            adaptive = False
            r_cuff_in_pre = [
                item for item in cuff_config["params"] if item["name"] == "_".join(["r_cuff_in_pre", cuff_code])
            ][0]
            if r_cuff_in_pre.get("adaptive"):
                adaptive = r_cuff_in_pre["adaptive"]

            if not adaptive:
                r_i_str: str = r_cuff_in_pre["expression"]
                r_i: float = Quantity(
                    Quantity(r_i_str.translate(r_i_str.maketrans("", "", " []")), scale="m"),
                    scale="um",
                ).real  # [um] (scaled from any arbitrary length unit)
            else:
                r_i_str = self.choose_diameter_pre(r_cuff_in_pre, r_f)

            r_i: float = Quantity(
                Quantity(r_i_str.translate(r_i_str.maketrans('', '', ' []')), scale='m'),
                scale='um',
            ).real  # [um] (scaled from any arbitrary length unit)

            if r_i < r_f:
                fixed_point = cuff_config.get('fixed_point')
                if fixed_point is None:
                    raise KeyError(
                        "Cuff configuration file must specify a fixed point if expandable=true. "
                        "See Creating custom preset cuffs from instances of part primitives in the documentation"
                    )
                if fixed_point == 'clockwise_end':
                    theta_f = theta_i * (r_i / r_f)
                elif fixed_point == 'center':
                    theta_f = theta_i
            else:
                theta_f = theta_i

        return r_i, theta_f

    def choose_diameter_pre(self, r_cuff_in_pre, r_f):  # noqa: C901
        """Choose the pre expansion diameter of the cuff based on the cuff expansion radius.

        :param r_cuff_in_pre: parameter for pre expansion radius of cuff (dict) from cuff config file
        :param r_f: cuff expansion radius
        :raises IncompatibleParametersError: if the parameters are not compatible in the cuff config file
        :return: r_i: pre expansion radius
        """
        bounds = []
        for param_option in r_cuff_in_pre["condition"]:
            r_min_str, r_max_str = (
                param_option["min"]["value"],
                param_option["max"]["value"],
            )
            r_min_ix, r_max_ix = (
                param_option["min"]["inclusive"],
                param_option["max"]["inclusive"],
            )
            parameter = param_option["parameter"]

            if r_min_str is not None:
                r_min: float = Quantity(
                    Quantity(
                        r_min_str.translate(r_min_str.maketrans("", "", " []")),
                        scale="m",
                    ),
                    scale="um",
                ).real  # [um] (scaled from any arbitrary length unit)
            else:
                r_min = None

            if r_max_str is not None:
                r_max: float = Quantity(
                    Quantity(
                        r_max_str.translate(r_max_str.maketrans("", "", " []")),
                        scale="m",
                    ),
                    scale="um",
                ).real  # [um] (scaled from any arbitrary length unit)
            else:
                r_max = None

            bounds.append((r_min, r_max, r_min_ix, r_max_ix, parameter))

        # check that none of the conditions have double Nones
        if any(bound[0] is None and bound[1] is None for bound in bounds):
            raise IncompatibleParametersError("Cuff configuration file has a condition with double Nones. ")

        # check that there is only one max with None, and one min with None
        if [bound[0] is None for bound in bounds].count(True) > 1 or [bound[1] is None for bound in bounds].count(
            True
        ) > 1:
            raise IncompatibleParametersError(
                "Cuff configuration file has more than one condition with None for min or max. "
            )

        # find index of upper and lower bound conditions
        lower_index = [x for x, y in enumerate(bounds) if y[0] is None][0]
        upper_index = [x for x, y in enumerate(bounds) if y[1] is None][0]
        lower = bounds[lower_index]
        upper = bounds[upper_index]

        # put max of None at end, and min of None at beginning
        bounds_indices = sorted([lower_index, upper_index], reverse=True)
        for idx in bounds_indices:
            if idx < len(bounds):
                bounds.pop(idx)

        if len(bounds) > 1:
            bounds.sort(key=lambda tmp: tmp[0])

        bounds_final = [lower, *bounds, upper]

        condition_match_count = 0
        r_cuff_in_parameter = None
        for r_min, r_max, r_min_ix, r_max_ix, parameter in bounds_final:
            if r_min_ix and r_max_ix:
                if r_min is None:
                    if r_f <= r_max:
                        r_cuff_in_parameter: str = parameter
                        condition_match_count += 1
                elif r_max is None:
                    if r_f >= r_min:
                        r_cuff_in_parameter: str = parameter
                        condition_match_count += 1
                elif r_min <= r_f <= r_max:
                    r_cuff_in_parameter: str = parameter
                    condition_match_count += 1
            elif r_min_ix and not r_max_ix:
                if r_min is None:
                    if r_f < r_max:
                        r_cuff_in_parameter: str = parameter
                        condition_match_count += 1
                elif r_max is None:
                    if r_f >= r_min:
                        r_cuff_in_parameter: str = parameter
                        condition_match_count += 1
                elif r_min <= r_f < r_max:
                    r_cuff_in_parameter: str = parameter
                    condition_match_count += 1
            elif r_max_ix and not r_min_ix:
                if r_min is None:
                    if r_f <= r_max:
                        r_cuff_in_parameter: str = parameter
                        condition_match_count += 1
                elif r_max is None:
                    if r_f > r_min:
                        r_cuff_in_parameter: str = parameter
                        condition_match_count += 1
                elif r_min < r_f <= r_max:
                    r_cuff_in_parameter: str = parameter
                    condition_match_count += 1
            elif not r_min_ix and not r_max_ix:
                if r_min is None:
                    if r_f < r_max:
                        r_cuff_in_parameter: str = parameter
                        condition_match_count += 1
                elif r_max is None:
                    if r_f > r_min:
                        r_cuff_in_parameter: str = parameter
                        condition_match_count += 1
                elif r_min < r_f < r_max:
                    r_cuff_in_parameter: str = parameter
                    condition_match_count += 1

        if condition_match_count == 0:
            raise IncompatibleParametersError(
                "Cuff configuration file has no conditions that match the given parameters. "
            )

        if condition_match_count > 1:
            # conditions are not mutually exclusive in preset JSON file
            raise IncompatibleParametersError(
                "Cuff configuration file has more than one condition that matches the given parameters. "
            )

        return r_cuff_in_parameter

    def compute_electrical_parameters(self):
        """Compute electrical parameters for a given model.

        :raises NotImplementedError: An invalid mode is specified
        :return: self
        """
        # initialize Waveform object
        waveform = Waveform()

        # add model config to Waveform object, enabling it to generate waveforms
        waveform.add(SetupMode.OLD, Config.MODEL, self.configs[Config.MODEL.value])

        # compute rho and sigma from waveform instance
        if (
            self.configs[Config.MODEL.value].get('modes').get(PerineuriumResistivityMode.config.value)
            == PerineuriumResistivityMode.RHO_WEERASURIYA.value
        ):
            freq_double = self.configs[Config.MODEL.value].get('frequency')
            rho_double = waveform.rho_weerasuriya(freq_double)
            sigma_double = 1 / rho_double
            tmp = {
                'value': str(sigma_double),
                'label': f'RHO_WEERASURIYA @ {freq_double} Hz',
                'unit': '[S/m]',
            }
            self.configs[Config.MODEL.value]['conductivities']['perineurium'] = tmp

        elif (
            self.configs[Config.MODEL.value].get('modes').get(PerineuriumResistivityMode.config.value)
            == PerineuriumResistivityMode.MANUAL.value
        ):
            pass
        else:
            raise NotImplementedError("Rho perineurium method not implemented")

        return self

    def validate(self):
        """Check model parameters for validity.

        :raises IncompatibleParametersError: if distal medium exists and proximal is set as ground
        :return: self
        """
        if self.search(Config.MODEL, 'medium', 'distal', 'exist') and self.search(
            Config.MODEL, 'medium', 'proximal', 'distant_ground'
        ):
            raise IncompatibleParametersError("Proximal medium boundary cannot be ground if distal medium exists.")

        return self

    def write(self, path):
        """Write the config file to disk.

        :param path: path to write the config file to
        :return: self
        """
        Configurable.write(self.configs[Config.MODEL.value], path)
        return self
