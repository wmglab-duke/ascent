#!/usr/bin/env python3.7

"""Defines MockSample class.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""


import json
import os
import sys
import warnings
from io import BytesIO

import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import shapely.affinity
from shapely.geometry import Point, Polygon

from src.utils import Config, Configurable, IncompatibleParametersError, MorphologyError, PopulateMode


class MockSample(Configurable):
    """Use MockSample class to generate a synthetic nerve morphology inputs to ASCENT.

    (i.e., binary image masks of epineurium (n.tif), perineurium (c.tif), and endoneurium (i.tif),
    and scalebar (s.tif)).
    """

    def __init__(self):
        """Create a MockSample object."""
        # Initializes superclasses
        Configurable.__init__(self)

        self.fascicles: list[shapely.geometry.Point] = []
        self.nerve = shapely.geometry.Point

    @staticmethod
    def get_random_fascicle_loc(nerve):
        """Get a random point inside the nerve epineurium.

        :param nerve: The nerve ellipse.
        :return: A random point inside the polygon.
        """
        minx, miny, maxx, maxy = nerve.bounds
        p = Point(minx, miny)  # min point will not be in ellipse
        while not nerve.contains(p):
            p = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))

        return p.x, p.y

    @staticmethod
    def gen_ellipse(ell):
        """Generate an ellipse shapely object.

        :param ell: tuple of ((center_x, center_y), (a, b), angle); a is the major diameter of the ellipse,
                    b is the minor diameter
        :return: The ellipse shapely object.
        """
        # Unpack ellipse parameters
        cx, cy = ell[0]
        a, b = ell[1]
        theta = np.deg2rad(ell[2])
        # Construct ellipse parameterized by (a*cos(t), b*cos(t))
        t = np.linspace(0, 2 * np.pi, 65)
        xs = np.cos(t) * a
        ys = np.sin(t) * b
        # Rotate ellipse with rotation matrix
        rot_mat = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        ell_pts = np.dot(rot_mat, np.array([xs, ys]))
        ell_pts[0] += cx
        ell_pts[1] += cy
        return Polygon(ell_pts.T)

    @staticmethod
    def binary_mask_canvas(margin: float, size: float):
        """Create a binary mask canvas.

        :param margin: The margin around the edges of the canvas, scaled to the size of the canvas.
        :param size: The size of the canvas in microns.
        :return: The binary mask canvas.
        """
        plt.style.use('dark_background')
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_aspect('equal')
        plt.axis('off')
        ax.set_xlim(margin * -size / 2, margin * size / 2)
        ax.set_ylim(margin * -size / 2, margin * size / 2)
        return fig

    @staticmethod
    def add_ellipse_binary_mask(fig: plt.Figure, ell: shapely.geometry.polygon):
        """Add an ellipse to a binary mask.

        :param fig: The binary mask figure.
        :param ell: The ellipse being added to the binary mask.
        :return: The binary mask figure with the ellipse added.
        """
        ell_x, ell_y = ell.exterior.xy
        fig.axes[0].fill(ell_x, ell_y, 'w')
        return fig

    @staticmethod
    def add_scalebar_binary_mask(fig: plt.Figure, slength: int):
        """Add a scalebar to a binary mask.

        :param fig: The binary mask figure.
        :param slength: The length of the scalebar in microns.
        :return: The binary mask figure with the scalebar added.
        """
        fig.axes[0].plot([-slength / 2, slength / 2], [0, 0], '-w')
        return fig

    @staticmethod
    def write_binary_mask(fig: plt.Figure, dest: str, dpi: int):
        """Write a binary mask to a file.

        :param fig: The binary mask figure.
        :param dest: The destination file.
        :param dpi: The resolution of the binary mask.
        """

        def create_opencv_image_from_stringio(img_stream, cv2_img_flag=0):
            img_stream.seek(0)
            img_array = np.asarray(bytearray(img_stream.read()), dtype=np.uint8)
            return cv2.imdecode(img_array, cv2_img_flag)

        png = BytesIO()
        fig.savefig(png, dpi=dpi, format='png')
        png.seek(0)
        img = create_opencv_image_from_stringio(png)
        _, bw_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        cv2.imwrite(dest, bw_img)
        plt.show()

    def make_nerve(self):
        """Make the nerve.

        :return: self
        """
        # DEFINE NERVE
        # 1st elem = center point (x,y) coordinates
        # 2nd elem = the two semi-axis values (along x, along y)
        # 3rd elem = angle in degrees between x-axis of the Cartesian base
        #            and the corresponding semi-axis
        p = (0.0, 0.0)

        if 'a_nerve' not in list(self.configs['mock_sample']['nerve'].keys()):
            # a is the major diameter of the ellipse
            a: float = self.search(Config.MOCK_SAMPLE, 'nerve', 'a') / 2
        else:
            # backwards compatible: a_nerve is the major radius
            a: float = self.search(Config.MOCK_SAMPLE, 'nerve', 'a_nerve')

        if 'b_nerve' not in list(self.configs['mock_sample']['nerve'].keys()):
            # b is the minor diameter of the ellipse
            b: float = self.search(Config.MOCK_SAMPLE, 'nerve', 'b') / 2
        else:
            # backwards compatible: b_nerve is the minor radius
            b: float = self.search(Config.MOCK_SAMPLE, 'nerve', 'b_nerve')

        if 'rot_nerve' not in list(self.configs['mock_sample']['nerve'].keys()):
            rot: float = self.search(Config.MOCK_SAMPLE, 'nerve', 'rot')
        else:
            # backwards compatible
            rot: float = self.search(Config.MOCK_SAMPLE, 'nerve', 'rot_nerve')

        ellipse = (p, (a, b), rot)
        self.nerve = self.gen_ellipse(ellipse)
        return self

    def make_fascicles(self):
        """Make the fascicles based on input parameters.

        :return: self
        """
        populate_mode_name: str = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'mode')
        populate_mode: PopulateMode = [mode for mode in PopulateMode if str(mode).split('.')[-1] == populate_mode_name][
            0
        ]
        min_fascicle_separation: float = self.search(
            Config.MOCK_SAMPLE,
            PopulateMode.parameters.value,
            'min_fascicle_separation',
        )

        if populate_mode == PopulateMode.EXPLICIT:
            self.make_explicit_fascicles(min_fascicle_separation)

        elif populate_mode == PopulateMode.TRUNCNORM:
            self.make_truncnorm_fascicles(min_fascicle_separation)

        elif populate_mode == PopulateMode.UNIFORM:
            self.make_uniform_fascicles(min_fascicle_separation)

        return self

    def make_truncnorm_fascicles(self, min_fascicle_separation):
        """Make fascicles using a truncated normal distribution.

        :param min_fascicle_separation: The minimum separation between fascicles [microns].
        :raises ValueError: If an input parameter is outside the allowed range.
        :raises IncompatibleParametersError: If input parameters conflict with each other.
        """
        # choose fascicle area [um^2]: A = pi*(d/2)**2
        mu_fasc_diam: float = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'mu_fasc_diam')
        std_fasc_diam: float = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'std_fasc_diam')
        n_std_diam_limit: float = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'n_std_diam_limit')
        # choose fascicle eccentricity
        mu_fasc_ecc: float = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'mu_fasc_ecc')
        std_fasc_ecc: float = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'std_fasc_ecc')
        n_std_ecc_limit: float = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'n_std_ecc_limit')
        # choose number of fascicles
        num_fascicle_attempt: int = self.search(
            Config.MOCK_SAMPLE,
            PopulateMode.parameters.value,
            'num_fascicle_attempt',
        )
        # choose maximum number of iterations for program to attempt to place fascicle
        max_attempt_iter: int = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'max_attempt_iter')
        # get random.seed myseed from config
        myseed: int = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'seed')
        np.random.seed(myseed)
        # CALCULATE FASCICLE DIAMS DISTRIBUTION (as if circle, major and minor axes same length)
        if n_std_diam_limit == 0 and std_fasc_diam != 0:
            raise IncompatibleParametersError(
                "Conflicting input arguments for std_fasc_diam and n_std_diam_limit for TRUNCNORM method"
            )
        lower_fasc_diam = mu_fasc_diam - n_std_diam_limit * std_fasc_diam
        upper_fasc_diam = mu_fasc_diam + n_std_diam_limit * std_fasc_diam
        if lower_fasc_diam < 0:
            raise ValueError("lower_fasc_diam must be defined as >= 0 for TRUNCNORM method")
        fasc_diam_dist = stats.truncnorm(
            (lower_fasc_diam - mu_fasc_diam) / std_fasc_diam,
            (upper_fasc_diam - mu_fasc_diam) / std_fasc_diam,
            loc=mu_fasc_diam,
            scale=std_fasc_diam,
        )
        # CALCULATE FASCICLE ECCENTRICITY DISTRIBUTION
        if n_std_ecc_limit == 0 and std_fasc_ecc != 0:
            raise IncompatibleParametersError(
                "Conflicting input arguments for std_fasc_ecc and n_std_ecc_limit for TRUNCNORM method"
            )
        if mu_fasc_ecc >= 1:
            raise ValueError(
                "Mean eccentricity value exceeds 1. Eccentricity only defined in range [01) for TRUNCNORM method"
            )
        lower_fasc_ecc = mu_fasc_ecc - n_std_ecc_limit * std_fasc_ecc
        upper_fasc_ecc = mu_fasc_ecc + n_std_ecc_limit * std_fasc_ecc
        if upper_fasc_ecc >= 1:
            upper_fasc_ecc = 0.99
            upper_fasc_ecc_warning = (
                f"Eccentricity only defined in range (0,1], overwrote upper_fasc_ecc, now = {upper_fasc_ecc}"
            )
            warnings.warn(upper_fasc_ecc_warning, stacklevel=2)
        if lower_fasc_ecc < 0:
            lower_fasc_ecc = 0
            lower_fasc_ecc_warning = (
                f"Eccentricity only defined in range (0,1], overwrote lower_fasc_ecc, now = {lower_fasc_ecc}"
            )
            warnings.warn(lower_fasc_ecc_warning, stacklevel=2)
        fasc_ecc_dist = stats.truncnorm(
            (lower_fasc_ecc - mu_fasc_ecc) / std_fasc_ecc,
            (upper_fasc_ecc - mu_fasc_ecc) / std_fasc_ecc,
            loc=mu_fasc_ecc,
            scale=std_fasc_ecc,
        )
        self.make_fascicle_dimensions_orientations(
            fasc_diam_dist, fasc_ecc_dist, max_attempt_iter, min_fascicle_separation, num_fascicle_attempt
        )

    def make_uniform_fascicles(self, min_fascicle_separation):
        """Make fascicles using a uniform distribution.

        :param min_fascicle_separation: The minimum separation between fascicles [microns].
        :raises ValueError: If an input parameter is outside the allowed range.
        """
        max_attempt_iter = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'max_attempt_iter')
        # choose fascicle area [um^2]: A = pi*(d/2)**2
        lower_fasc_diam: float = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'lower_fasc_diam')
        upper_fasc_diam: float = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'upper_fasc_diam')
        # check that both lower_diam and upper_diam are positive, and upper_diam > lower_diam
        if lower_fasc_diam < 0:
            raise ValueError("lower_fasc_diam bound must be positive length for UNIFORM method")
        if lower_fasc_diam > upper_fasc_diam:
            raise ValueError("upper_fasc_diam bound must be >= lower_fasc_diam bound for UNIFORM method")
        lower_fasc_ecc: float = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'lower_fasc_ecc')
        upper_fasc_ecc: float = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'upper_fasc_ecc')
        if lower_fasc_ecc < 0:
            raise ValueError("Ellipse eccentricity lower_fasc_ecc must be >= 0 for UNIFORM method")
        if upper_fasc_ecc >= 1:
            raise ValueError("Ellipse eccentricity upper_fasc_ecc must be < 1 for UNIFORM method")
        # choose number of fascicles
        num_fascicle_attempt: int = self.search(
            Config.MOCK_SAMPLE,
            PopulateMode.parameters.value,
            'num_fascicle_attempt',
        )
        # get random.seed myseed from config
        myseed: int = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, 'seed')
        np.random.seed(myseed)
        # CALCULATE FASCICLE DIAMS DISTRIBUTION (as if circle, major and minor axes same length)
        fasc_diam_dist = stats.uniform(lower_fasc_diam, upper_fasc_diam - lower_fasc_diam)
        # CALCULATE FASCICLE ECCENTRICITY DISTRIBUTION
        fasc_ecc_dist = stats.uniform(lower_fasc_ecc, upper_fasc_ecc - lower_fasc_ecc)
        self.make_fascicle_dimensions_orientations(
            fasc_diam_dist, fasc_ecc_dist, max_attempt_iter, min_fascicle_separation, num_fascicle_attempt
        )

    def make_fascicle_dimensions_orientations(
        self, fasc_diam_dist, fasc_ecc_dist, max_attempt_iter, min_fascicle_separation, num_fascicle_attempt
    ):
        """Make fascicle dimensions and orientations.

        :param fasc_diam_dist: The distribution of fascicle diameters.
        :param fasc_ecc_dist: The distribution of fascicle eccentricities.
        :param max_attempt_iter: The maximum number of attempts to place fascicles.
        :param min_fascicle_separation: The minimum separation between fascicles [microns].
        :param num_fascicle_attempt: The number of fascicles to attempt to place.
        """
        # BASED ON CHOSEN DISTRIBUTION, MAKE FASCICLE DIMENSIONS AND ORIENTATIONS
        fasc_diams = np.sort(fasc_diam_dist.rvs(num_fascicle_attempt))[::-1].T
        fasc_areas = np.pi * (fasc_diams / 2) ** 2
        fasc_eccs = fasc_ecc_dist.rvs(num_fascicle_attempt)
        # CALCULATE FASCICLE ROTATIONS
        fasc_rots = [360 * np.random.random() for _ in range(num_fascicle_attempt)]
        # CALCULATE FASCICLE MAJOR AND MINOR AXES
        a_axes = [((area**2) / ((np.pi**2) * (1 - (ecc**2)))) ** (1 / 4) for area, ecc in zip(fasc_areas, fasc_eccs)]
        b_axes = [area / (np.pi * a_axis) for area, a_axis in zip(fasc_areas, a_axes)]
        # DEFINE/PLACE FASCICLES
        n_itr = []
        skipped_fascicles_index = []
        for i in range(num_fascicle_attempt):
            n_itr.append(0)

            while True:
                n_itr[i] += 1

                if n_itr[i] > max_attempt_iter:
                    skipped_fascicles_index.append(i)
                    break

                p = self.get_random_fascicle_loc(self.nerve)
                # 1st elem = center point (x,y) coordinates
                # 2nd elem = the two semi-axis values (along x, along y)
                # 3rd elem = angle in degrees between x-axis of the Cartesian base
                #            and the corresponding semi-axis
                ellipse = (p, (a_axes[i], b_axes[i]), fasc_rots[i])
                fascicle_attempt = self.gen_ellipse(ellipse)

                chk = 0
                if fascicle_attempt.buffer(min_fascicle_separation).boundary.intersects(self.nerve.boundary):
                    chk = 1

                if any(fasc.buffer(min_fascicle_separation).intersects(fascicle_attempt) for fasc in self.fascicles):
                    chk = 1

                if chk == 0:
                    self.fascicles.append(fascicle_attempt)
                    break
        # print to console any fascicle diameters that were skipped
        if len(self.fascicles) < num_fascicle_attempt:
            print('ATTENTION: Either re-run program or reduce #/size/separation distance fascicles')
            print(
                f'User requested {num_fascicle_attempt} fascicles, but program could only place {len(self.fascicles)}'
            )
        self.configs['mock_sample'][PopulateMode.parameters.value]['num_fascicle_placed'] = len(self.fascicles)

    def make_explicit_fascicles(self, min_fascicle_separation):
        """Make fascicles explicitly using the fascicle coordinates in the config file.

        :param min_fascicle_separation: The minimum separation between fascicles [microns].
        :raises MorphologyError: If the fascicles are too close together
        """
        fascs_explicit = self.search(Config.MOCK_SAMPLE, PopulateMode.parameters.value, "Fascicles")
        fasc_centroid_xs = [0] * len(fascs_explicit)
        fasc_centroid_ys = [0] * len(fascs_explicit)
        fasc_as = [0] * len(fascs_explicit)
        fasc_bs = [0] * len(fascs_explicit)
        fasc_rots = [0] * len(fascs_explicit)
        # load ellipse information for all fascicles
        for fasc_ind, fascicle in enumerate(fascs_explicit):
            fasc_centroid_xs[fasc_ind] = fascicle.get('centroid_x')
            fasc_centroid_ys[fasc_ind] = fascicle.get('centroid_y')
            fasc_as[fasc_ind] = fascicle.get('a') / 2
            fasc_bs[fasc_ind] = fascicle.get('b') / 2
            fasc_rots[fasc_ind] = fascicle.get('rot')
        if any(x in list(self.configs['mock_sample']['nerve'].keys()) for x in ['a_nerve' or 'b_nerve']):
            reply = (
                input(
                    'Looks like might be using an old MockSample JSON template. \n'
                    'The ellipse parameters (a,b) for fascicles now are the full width major and minor axes \n'
                    '(i.e., analogous to circle diameter rather than radii). Make sure your values are set \n'
                    'appropriately. This change is new in v1.1.0 to be consistent with the ellipse parameters \n'
                    '(a,b) in Sample which are full width ellipse major/minor axes lengths.\n\n'
                    'See config/templates/mock_sample.json for new template and avoid this message.\n'
                    'Would you like to proceed with the values currently set for (a,b) as diameter? [y/N] '
                )
                .lower()
                .strip()
            )
            if reply[0] != 'y':
                print('Please make changes to have (a,b) values be diameter of ellipse and re-run.\n')
                sys.exit()
            else:
                print('Proceeding with existing MockSample.\n')

            # You are using an old MockSample JSON template. The ellipse parameters for fascicles now are the major
            # and minor diameters. Make sure you values are set appropriately. This change is new in v.1.1.0 to
            # be consistent with the ellipse parameters in Sample. Would you like to proceed? y/n
        # check that the loaded fascicles are far enough apart from each other and the nerve
        for fasc_ind in range(len(fascs_explicit)):
            p = (fasc_centroid_xs[fasc_ind], fasc_centroid_ys[fasc_ind])
            ellipse = (
                p,
                (fasc_as[fasc_ind], fasc_bs[fasc_ind]),
                fasc_rots[fasc_ind],
            )
            fascicle_attempt = self.gen_ellipse(ellipse)

            chk = 0
            # check to make sure the fascicle is within the nerve
            if not fascicle_attempt.within(self.nerve):
                chk = 1

            # check for fascicle:nerve intersection with addition of next fascicle
            if fascicle_attempt.buffer(min_fascicle_separation).boundary.intersects(self.nerve.boundary):
                chk = 1

            # check for fascicle:fascicle intersection with addition of next fascicle
            if any(fasc.buffer(min_fascicle_separation).intersects(fascicle_attempt) for fasc in self.fascicles):
                chk = 1

            # if all checks passed, add the fascicle to the list
            if chk == 0:
                self.fascicles.append(fascicle_attempt)
        # since explicitly defined, user made an error if not all fascicles were placed.
        if len(self.fascicles) < len(fascs_explicit):
            raise MorphologyError(
                "Explicit fascicle positions are too close to each other the nerve boundary, "
                "or are outside the boundary for EXPLICIT method"
            )

    def make_masks(self):
        """Make the masks for the fascicles and nerve.

        :raises ValueError: If fig_margin is too small
        :return: self
        """
        project_path = os.getcwd()
        sample_str = self.search(Config.MOCK_SAMPLE, 'global', 'NAME')
        sample_dir = os.path.join(project_path, 'input', sample_str)

        if not os.path.exists(sample_dir):
            os.mkdir(sample_dir)

        with open(os.path.join(sample_dir, 'mock.json'), "w") as handle:
            handle.write(json.dumps(self.configs['mock_sample'], indent=2))

        if 'a_nerve' not in list(self.configs['mock_sample']['nerve'].keys()):
            # a is the major diameter of the ellipse
            a: float = self.search(Config.MOCK_SAMPLE, 'nerve', 'a') / 2
        else:
            # backwards compatible: a_nerve is the major radius
            a: float = self.search(Config.MOCK_SAMPLE, 'nerve', 'a_nerve')

        if 'b_nerve' not in list(self.configs['mock_sample']['nerve'].keys()):
            # b is the minor diameter of the ellipse
            b: float = self.search(Config.MOCK_SAMPLE, 'nerve', 'b') / 2
        else:
            # backwards compatible: b_nerve is the minor radius
            b: float = self.search(Config.MOCK_SAMPLE, 'nerve', 'b_nerve')

        scalebar_length: int = self.search(Config.MOCK_SAMPLE, 'scalebar_length')
        max_diam = max(scalebar_length, 2 * max(a, b))

        fig_margin: float = self.search(Config.MOCK_SAMPLE, 'figure', 'fig_margin')

        if fig_margin < 1:
            raise ValueError("fig_margin < 1 so the ellipse for the nerve will not fit on the canvas")

        fig_dpi: int = self.search(Config.MOCK_SAMPLE, 'figure', 'fig_dpi')

        # MAKE BINARY IMAGES FOR INPUT TO PIPELINE
        # NERVE BINARY IMAGE
        dest_n = os.path.join(project_path, sample_dir, 'n.tif')
        figure_n = self.binary_mask_canvas(fig_margin, max_diam)
        figure_n = self.add_ellipse_binary_mask(figure_n, self.nerve)
        self.write_binary_mask(figure_n, dest_n, fig_dpi)

        # FASCICLES (inners) BINARY IMAGE
        dest_i = os.path.join(project_path, sample_dir, 'i.tif')
        figure_i = self.binary_mask_canvas(fig_margin, max_diam)
        for fascicle in self.fascicles:
            if fascicle is not None and fascicle.exterior is not None:
                figure_i = self.add_ellipse_binary_mask(figure_i, fascicle)
        self.write_binary_mask(figure_i, dest_i, fig_dpi)

        # SCALEBAR BINARY IMAGE
        dest_s = os.path.join(project_path, sample_dir, 's.tif')
        figure_s = self.binary_mask_canvas(fig_margin, max_diam)
        figure_s = self.add_scalebar_binary_mask(figure_s, scalebar_length)
        self.write_binary_mask(figure_s, dest_s, fig_dpi)

        return self
