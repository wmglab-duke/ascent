#!/usr/bin/env python3.7

import json
import os
from typing import Tuple

import sys
import time
import warnings
from io import BytesIO

import scipy.stats as stats
import numpy as np

from shapely.geometry.point import Point
import shapely.affinity

import matplotlib.pyplot as plt

import cv2

# START timer
from src.core import MockSample
from src.utils import *

start = time.time()

if len(sys.argv) != 2:
    print('INVALID number of arguments to mock_morphology_generator.py')
    exit(1)

# load mock sample configuration
mock_config = os.path.join('config', 'user', 'mock_samples', '{}.json'.format(sys.argv[1]))
exceptions_file = os.path.join('config', 'system', 'exceptions.json')

with open(exceptions_file, "r") as handle:
    exceptions_config: dict = json.load(handle)

mock_sample = MockSample(exceptions_config)
mock_sample.add(SetupMode.NEW, Config.MOCK_SAMPLE, mock_config)
mock_sample.make_nerve()
mock_sample.make_fascicles()
mock_sample.make_masks()

# # https://gis.stackexchange.com/questions/6412/generate-points-that-lie-inside-polygon
# def get_random_point_in_polygon(poly):
#     minx, miny, maxx, maxy = poly.bounds
#     while True:
#         p = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
#         if poly.contains(p):
#             return p
#
#
# # https://inneka.com/ml/opencv/how-to-read-image-from-in-memory-buffer-stringio-or-from-url-with-opencv-python-library/
# def create_opencv_image_from_stringio(img_stream, cv2_img_flag=0):
#     img_stream.seek(0)
#     img_array = np.asarray(bytearray(img_stream.read()), dtype=np.uint8)
#     return cv2.imdecode(img_array, cv2_img_flag)
#
#
# def gen_ellipse(ell):
#     ell_obj = shapely.geometry.Point(ell[0]).buffer(1)
#     ell_obj = shapely.affinity.scale(ell_obj, ell[1][0], ell[1][1], 0, ell[0])
#     ell_obj = shapely.affinity.rotate(ell_obj, ell[2], origin='center', use_radians=False)
#     return ell_obj
#
#
# def binary_mask_canvas(margin: float, size: float):
#     plt.style.use('dark_background')
#     fig = plt.figure()
#     ax = fig.add_subplot(111)
#     ax.set_aspect('equal')
#     plt.axis('off')
#     ax.set_xlim(margin * -size / 2, margin * size / 2)
#     ax.set_ylim(margin * -size / 2, margin * size / 2)
#     return fig
#
#
# def add_ellipse_binary_mask(fig: plt.figure(), ell: Tuple[shapely.geometry.Point, Tuple[float, float], float]):
#     ell_x, ell_y = ell.exterior.xy
#     fig.axes[0].fill(ell_x, ell_y, 'w')
#     return fig
#
#
# def add_scalebar_binary_mask(fig: plt.figure(), slength: int):
#     fig.axes[0].plot([-slength/2, slength/2], [0, 0], '-w')
#     return fig
#
#
# def write_binary_mask(fig: plt.figure(), dest: str, dpi: int):
#     png = BytesIO()
#     fig.savefig(png, dpi=dpi, format='png')
#     png.seek(0)
#     img = create_opencv_image_from_stringio(png)
#     _, bw_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
#     cv2.imwrite(dest, bw_img)



# with open(mock_file, "r") as handle:
#     mockConfig: dict = json.load(handle)




# load global parameters
# global_params: dict = mockConfig.get('global')
#
# # define sample ID
# sample_str = global_params.get('sample_str')
#
# project_path = os.getcwd()
# sample_dir = os.path.join(project_path, 'data', 'input', 'samples', sample_str)
# if not os.path.exists(os.path.join(project_path, sample_dir)):
#     os.makedirs(os.path.join(project_path, sample_dir))
#
# # define scalebar length
# scalebar_length = global_params.get('scalebar_length')
#
# # choose nerve diameter [um]
# a_nerve = global_params.get("a_nerve")
# b_nerve = global_params.get("b_nerve")
# rot_nerve = global_params.get("rot_nerve")
# max_diam = 2*max(a_nerve, b_nerve)
#
# # get method for making nerve (either "truncnorm" OR "uniform" OR "explicit")
# method = global_params.get("method")
#
# # choose minumum fascicle distance
# min_fascicle_separation = global_params.get('min_fascicle_separation')
#
# # figure settings
# fig_margin = global_params.get('fig_margin')
# fig_dpi = global_params.get('fig_dpi')
#
# # DEFINE NERVE
# # 1st elem = center point (x,y) coordinates
# # 2nd elem = the two semi-axis values (along x, along y)
# # 3rd elem = angle in degrees between x-axis of the Cartesian base
# #            and the corresponding semi-axis
# p = Point(0.0, 0.0)
# ellipse = (p, (a_nerve, b_nerve), rot_nerve)
# nerve = gen_ellipse(ellipse)
#
# fascicles = []
# # POPULATE NERVE
# if method != "explicit":
#     # for each of the following methods, load parameters to define the distribution
#     # (our examples use the SciPy statistics package)
#     # and then create distributions for the fascicle diameters and eccentricities:
#     # - fasc_diam_dist
#     # - fasc_ecc_dist
#
#     # TRUNCNORM
#     # truncated normal distribution (normal, but bounded above and below by same number of standard deviations)
#     if method == "truncnorm":
#         truncnorm_params: dict = mockConfig.get('truncnorm')
#
#         # choose fascicle area [um^2]: A = pi*(d/2)**2
#         mu_fasc_diam = truncnorm_params.get('mu_fasc_diam')
#         std_fasc_diam = truncnorm_params.get('std_fasc_diam')
#         n_std_diam_limit = truncnorm_params.get('n_std_diam_limit')
#
#         # choose fascicle eccentricity (
#         mu_fasc_ecc = truncnorm_params.get('mu_fasc_ecc')
#         std_fasc_ecc = truncnorm_params.get('std_fasc_ecc')
#         n_std_ecc_limit = truncnorm_params.get('n_std_ecc_limit')
#
#         # choose number of fascicles
#         num_fascicle_attempt = truncnorm_params.get('num_fascicle_attempt')
#
#         # choose maximum number of iterations for program to attempt to place fascicle
#         max_attempt_iter = truncnorm_params.get('max_attempt_iter')
#
#         # get random.seed myseed from config
#         myseed = truncnorm_params.get('seed')
#         np.random.seed(myseed)
#
#         # CALCULATE FASCICLE DIAMS (as if circle, major and minor axes same length)
#         if n_std_diam_limit == 0 and std_fasc_diam != 0:
#             raise Exception('Conflicting input arguments for std_fasc_diam and n_std_diam_limit')
#
#         if std_fasc_diam == 0:
#             fasc_diams = np.ones(num_fascicle_attempt) * mu_fasc_diam
#             upper_fasc_diam = mu_fasc_diam
#             lower_fasc_diam = mu_fasc_diam
#         else:
#             lower_fasc_diam, upper_fasc_diam = mu_fasc_diam - n_std_diam_limit * std_fasc_diam, \
#                                                mu_fasc_diam + n_std_diam_limit * std_fasc_diam
#
#             if lower_fasc_diam < 0:
#                 raise Exception('lower_fasc_diam must be defined as >= 0')
#
#             fasc_diam_dist = stats.truncnorm((lower_fasc_diam - mu_fasc_diam) / std_fasc_diam,
#                                              (upper_fasc_diam - mu_fasc_diam) / std_fasc_diam,
#                                              loc=mu_fasc_diam,
#                                              scale=std_fasc_diam)
#
#         # CALCULATE FASCICLE ECCENTRICITY
#         if n_std_ecc_limit == 0 and std_fasc_ecc != 0:
#             raise Exception('Conflicting input arguments for std_fasc_ecc and n_std_ecc_limit')
#
#         if mu_fasc_ecc >= 1:
#             raise Exception('Mean eccentricity value exceeds 1. Eccentricity only defined in range [0,1).')
#
#         if std_fasc_ecc == 0:
#             fasc_eccs = np.ones(num_fascicle_attempt) * mu_fasc_ecc
#             upper_fasc_ecc = mu_fasc_ecc
#             lower_fasc_ecc = mu_fasc_ecc
#         else:
#             lower_fasc_ecc, upper_fasc_ecc = mu_fasc_ecc - n_std_ecc_limit * std_fasc_ecc, \
#                                              mu_fasc_ecc + n_std_ecc_limit * std_fasc_ecc
#             if upper_fasc_ecc >= 1:
#                 upper_fasc_ecc = 0.99
#                 upper_fasc_ecc_warning = "Eccentricity only defined in range (0,1], " \
#                                          "overwrote upper_fasc_ecc, now = {}".format(upper_fasc_ecc)
#                 warnings.warn(upper_fasc_ecc_warning)
#
#             if lower_fasc_ecc < 0:
#                 lower_fasc_ecc = 0
#                 lower_fasc_ecc_warning = "Eccentricity only defined in range (0,1], " \
#                                          "overwrote lower_fasc_ecc, now = {}".format(lower_fasc_ecc)
#                 warnings.warn(lower_fasc_ecc_warning)
#
#             fasc_ecc_dist = stats.truncnorm((lower_fasc_ecc - mu_fasc_ecc) / std_fasc_ecc,
#                                             (upper_fasc_ecc - mu_fasc_ecc) / std_fasc_ecc,
#                                             loc=mu_fasc_ecc,
#                                             scale=std_fasc_ecc)
#
#     # UNIFORM
#     # random distribution (uniform probability across range) between upper and lower bound
#     elif method == "uniform":
#         uniform_params: dict = mockConfig.get('uniform')
#
#         # choose fascicle area [um^2]: A = pi*(d/2)**2
#         lower_fasc_diam = uniform_params.get('lower_fasc_diam')
#         upper_fasc_diam = uniform_params.get('upper_fasc_diam')
#
#         # check that both lower_diam and upper_diam are positive, and upper_diam > lower_diam
#         if lower_fasc_diam < 0:
#             raise Exception('lower_fasc_diam bound must be positive length')
#         if lower_fasc_diam > upper_fasc_diam:
#             raise Exception('upper_fasc_diam bound must be >= lower_fasc_diam bound')
#
#         lower_fasc_ecc = uniform_params.get('lower_fasc_ecc')
#         upper_fasc_ecc = uniform_params.get('upper_fasc_ecc')
#
#         if lower_fasc_ecc < 0:
#             raise Exception('Ellipse eccentricity lower_fasc_ecc must be >= 0')
#         if upper_fasc_ecc >= 1:
#             raise Exception('Ellipse eccentricity upper_fasc_ecc must be < 1')
#
#         # choose number of fascicles
#         num_fascicle_attempt = uniform_params.get('num_fascicle_attempt')
#
#         # choose maximum number of iterations for program to attempt to place fascicle
#         max_attempt_iter = uniform_params.get('max_attempt_iter')
#
#         # get random.seed myseed from config
#         myseed = uniform_params.get('seed')
#         np.random.seed(myseed)
#
#         fasc_diam_dist = stats.uniform(lower_fasc_diam, upper_fasc_diam - lower_fasc_diam)
#         fasc_ecc_dist = stats.uniform(lower_fasc_ecc, upper_fasc_ecc - lower_fasc_ecc)
#
#     # BASED ON CHOSEN DISTRIBUTION, MAKE FASCICLE DIMENSIONS AND ORIENTATIONS
#     fasc_diams = np.sort(fasc_diam_dist.rvs(num_fascicle_attempt))[::-1].T
#     fasc_areas = np.pi * (fasc_diams / 2) ** 2
#
#     fasc_eccs = fasc_ecc_dist.rvs(num_fascicle_attempt)
#
#     # CALCULATE FASCICLE ROTATIONS
#     fasc_rots = [360 * np.random.random() for _ in range(num_fascicle_attempt)]
#
#     # CALCULATE FASCICLE MAJOR AND MINOR AXES
#     a_axes = [((area ** 2) / ((np.pi ** 2) * (1 - (ecc ** 2)))) ** (1 / 4) for area, ecc in zip(fasc_areas, fasc_eccs)]
#     b_axes = [area / (np.pi * a_axis) for area, a_axis in zip(fasc_areas, a_axes)]
#
#     n_itr = []
#     skipped_fascicles_index = []
#
#     # DEFINE/PLACE FASCICLES
#     for i in range(num_fascicle_attempt):
#         n_itr.append(0)
#
#         while True:
#             n_itr[i] += 1
#
#             if n_itr[i] > max_attempt_iter:
#                 skipped_fascicles_index.append(i)
#                 break
#
#             # https://gis.stackexchange.com/questions/243459/drawing-ellipse-with-shapely
#             p = get_random_point_in_polygon(nerve)
#             # 1st elem = center point (x,y) coordinates
#             # 2nd elem = the two semi-axis values (along x, along y)
#             # 3rd elem = angle in degrees between x-axis of the Cartesian base
#             #            and the corresponding semi-axis
#             ellipse = (p, (a_axes[i], b_axes[i]), fasc_rots[i])
#             fascicle_attempt = gen_ellipse(ellipse)
#
#             chk = 0
#             if fascicle_attempt.buffer(min_fascicle_separation).boundary.intersects(nerve.boundary):
#                 chk = 1
#
#             if any([fasc.buffer(min_fascicle_separation).intersects(fascicle_attempt) for fasc in fascicles]):
#                 chk = 1
#
#             if chk == 0:
#                 fascicles.append(fascicle_attempt)
#                 break
#
#     # print to console any fascicle diameters that were skipped
#     if len(fascicles) < num_fascicle_attempt:
#         print('ATTENTION: Either re-run program or reduce #/size/separation distance fascicles')
#         print(
#             'User requested {} fascicles, but program could only place {}'.format(num_fascicle_attempt, len(fascicles)))
#
#     mockConfig['num_fascicle_placed'] = len(fascicles)
#
#     with open(os.path.join(project_path, sample_dir, 'mock.json'), "w") as handle:
#         handle.write(json.dumps(mockConfig, indent=2))
#
#     # N = stats.norm(loc=mu_fasc, scale=std_fasc)
#     # fig, ax = plt.subplots(2, sharex=True)
#     # ax[0].hist(X.rvs(10000), density=True)
#     # ax[1].hist(N.rvs(10000), density=True)
#     # plt.show

# elif method == "explicit":
#     fascs_explicit = mockConfig.get('explicit').get('Fascicles')
#
#     fasc_centroid_xs = [0] * len(fascs_explicit)
#     fasc_centroid_ys = [0] * len(fascs_explicit)
#     fasc_as = [0] * len(fascs_explicit)
#     fasc_bs = [0] * len(fascs_explicit)
#     fasc_rots = [0] * len(fascs_explicit)
#
#     # load ellipse information for all fascicles
#     for fasc_ind, fascicle in enumerate(fascs_explicit):
#         fasc_centroid_xs[fasc_ind] = fascicle.get('centroid_x')
#         fasc_centroid_ys[fasc_ind] = fascicle.get('centroid_y')
#         fasc_as[fasc_ind] = fascicle.get('a')
#         fasc_bs[fasc_ind] = fascicle.get('b')
#         fasc_rots[fasc_ind] = fascicle.get('rot')
#
#     # check that the loaded fascicles are far enough apart from each other and the nerve
#     for fasc_ind, fascicle in enumerate(fascs_explicit):
#         p = (fasc_centroid_xs[fasc_ind], fasc_centroid_ys[fasc_ind])
#         ellipse = (p, (fasc_as[fasc_ind], fasc_bs[fasc_ind]), fasc_rots[fasc_ind])
#         fascicle_attempt = gen_ellipse(ellipse)
#
#         chk = 0
#         # check to make sure the fascicle is within the nerve
#         if not fascicle_attempt.within(nerve):
#             chk = 1
#
#         # check for fascicle:nerve intersection with addition of next fascicle
#         if fascicle_attempt.buffer(min_fascicle_separation).boundary.intersects(nerve.boundary):
#             chk = 1
#
#         # check for fascicle:fascicle intersection with addition of next fascicle
#         if any([fasc.buffer(min_fascicle_separation).intersects(fascicle_attempt) for fasc in fascicles]):
#             chk = 1
#
#         # if all checks passed, add the fascicle to the list
#         if chk == 0:
#             fascicles.append(fascicle_attempt)
#
#     # since explicitly defined, user made an error if not all fascicles were placed.
#     if len(fascicles) < len(fascs_explicit):
#         raise Exception('Explicit fascicle positions are too close to each other, the nerve boundary, '
#                         'or are outside the nerve.')

# # MAKE BINARY IMAGES FOR INPUT TO PIPELINE
# # NERVE BINARY IMAGE
# dest_n = os.path.join(project_path, sample_dir, '{}_0_0_n.tif'.format(sample_str))
# figure_n = binary_mask_canvas(fig_margin, max_diam)
# figure_n = add_ellipse_binary_mask(figure_n, nerve)
# write_binary_mask(figure_n, dest_n, fig_dpi)
#
# # FASCICLES (inners) BINARY IMAGE
# dest_i = os.path.join(project_path, sample_dir, '{}_0_0_i.tif'.format(sample_str))
# figure_i = binary_mask_canvas(fig_margin, max_diam)
# for fascicle in fascicles:
#     if fascicle is not None and fascicle.exterior is not None:
#         figure_i = add_ellipse_binary_mask(figure_i, fascicle)
# write_binary_mask(figure_i, dest_i, fig_dpi)
#
# # SCALEBAR BINARY IMAGE
# dest_s = os.path.join(project_path, sample_dir, '{}_0_0_s.tif'.format(sample_str))
# figure_s = binary_mask_canvas(fig_margin, max_diam)
# figure_s = add_scalebar_binary_mask(figure_s, scalebar_length)
# write_binary_mask(figure_s, dest_s, fig_dpi)

# END timer
end = time.time()
print('\nruntime: {}'.format(end - start))

# cleanup for console viewing/inspecting
del start, end
