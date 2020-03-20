#!/usr/bin/env python3.7

import json
import os
import random
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


# https://gis.stackexchange.com/questions/6412/generate-points-that-lie-inside-polygon
def get_random_point_in_polygon(poly):
    minx, miny, maxx, maxy = poly.bounds
    while True:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if poly.contains(p):
            return p


# https://inneka.com/ml/opencv/how-to-read-image-from-in-memory-buffer-stringio-or-from-url-with-opencv-python-library/
def create_opencv_image_from_stringio(img_stream, cv2_img_flag=0):
    img_stream.seek(0)
    img_array = np.asarray(bytearray(img_stream.read()), dtype=np.uint8)
    return cv2.imdecode(img_array, cv2_img_flag)


# START timer
start = time.time()

if len(sys.argv) != 2:
    print('INVALID number of arguments to mock_morphology_generator.py')
    exit(1)

mock_file = os.path.join('config', 'user', 'mock_samples', '{}.json'.format(sys.argv[1]))
with open(mock_file, "r") as handle:
    mockConfig: dict = json.load(handle)

# define sample ID
sample_str = mockConfig.get('global').get('sample_str')

project_path = os.getcwd()
sample_dir = os.path.join(project_path, 'data', 'input', 'samples', sample_str)
if not os.path.exists(os.path.join(project_path, sample_dir)):
    os.makedirs(os.path.join(project_path, sample_dir))

# define scalebar length
scalebar_length = mockConfig.get('global').get('scalebar_length')

# choose nerve diameter [um]
d_nerve = mockConfig.get('global').get("d_nerve")

# get method for making nerve (either "probabilistic" OR "explicit"
method = mockConfig.get('global').get("method")

# choose minumum fascicle distance
min_fascicle_separation = mockConfig.get('global').get('min_fascicle_separation')

# figure settings
fig_margin = mockConfig.get('global').get('fig_margin')
fig_dpi = mockConfig.get('global').get('fig_dpi')

if method == "probabilistic":
    # choose fascicle area [um^2]: A = pi*(d/2)**2
    mu_fasc_diam = mockConfig.get('probabilistic').get('mu_fasc_diam')
    std_fasc_diam = mockConfig.get('probabilistic').get('std_fasc_diam')
    n_std_diam_limit = mockConfig.get('probabilistic').get('n_std_diam_limit')

    # choose number of fascicles
    num_fascicle_attempt = mockConfig.get('probabilistic').get('num_fascicle_attempt')

    # choose fascicle eccentricity (
    mu_fasc_ecc = mockConfig.get('probabilistic').get('mu_fasc_ecc')
    std_fasc_ecc = mockConfig.get('probabilistic').get('std_fasc_ecc')
    n_std_ecc_limit = mockConfig.get('probabilistic').get('n_std_ecc_limit')

    # choose maximum number of iterations for program to attempt to place fascicle
    max_attempt_iter = mockConfig.get('probabilistic').get('max_attempt_iter')

    # get random.seed myseed from config
    myseed = mockConfig.get('probabilistic').get('seed')
    random.seed(myseed)

    # CALCULATE FASCICLE DIAMS (as if circle, major and minor axes same length)
    if n_std_diam_limit == 0 and std_fasc_diam != 0:
        raise Exception('Conflicting input arguments for std_fasc_diam and n_std_diam_limit')

    if std_fasc_diam == 0:
        fasc_diams = np.ones(num_fascicle_attempt) * mu_fasc_diam
        upper_fasc_diam = mu_fasc_diam
        lower_fasc_diam = mu_fasc_diam
    else:
        lower_fasc_diam, upper_fasc_diam = mu_fasc_diam - n_std_diam_limit * std_fasc_diam, \
                                           mu_fasc_diam + n_std_diam_limit * std_fasc_diam
        fasc_diam_dist = stats.truncnorm((lower_fasc_diam - mu_fasc_diam) / std_fasc_diam,
                                         (upper_fasc_diam - mu_fasc_diam) / std_fasc_diam,
                                         loc=mu_fasc_diam,
                                         scale=std_fasc_diam)

        fasc_diams = np.sort(fasc_diam_dist.rvs(num_fascicle_attempt))[::-1].T

    fasc_areas = np.pi * (fasc_diams / 2) ** 2

    # CALCULATE FASCICLE ECCENTRICITY
    if n_std_ecc_limit == 0 and std_fasc_ecc != 0:
        raise Exception('Conflicting input arguments for std_fasc_ecc and n_std_ecc_limit')

    if mu_fasc_ecc >= 1:
        raise Exception('Mean eccentricity value exceeds 1. Eccentricity only defined in range [0,1).')

    if std_fasc_ecc == 0:
        fasc_eccs = np.ones(num_fascicle_attempt) * mu_fasc_ecc
        upper_fasc_ecc = mu_fasc_ecc
        lower_fasc_ecc = mu_fasc_ecc
    else:
        lower_fasc_ecc, upper_fasc_ecc = mu_fasc_ecc - n_std_ecc_limit * std_fasc_ecc, \
                                         mu_fasc_ecc + n_std_ecc_limit * std_fasc_ecc
        if upper_fasc_ecc >= 1:
            upper_fasc_ecc = 0.99
            upper_fasc_ecc_warning = "Eccentricity only defined in range (0,1], " \
                                     "overwrote upper_fasc_ecc, now = {}".format(upper_fasc_ecc)
            warnings.warn(upper_fasc_ecc_warning)

        if lower_fasc_ecc < 0:
            lower_fasc_ecc = 0
            lower_fasc_ecc_warning = "Eccentricity only defined in range (0,1], " \
                                     "overwrote lower_fasc_ecc, now = {}".format(lower_fasc_ecc)
            warnings.warn(lower_fasc_ecc_warning)

        fascEccDist = stats.truncnorm((lower_fasc_ecc - mu_fasc_ecc) / std_fasc_ecc,
                                      (upper_fasc_ecc - mu_fasc_ecc) / std_fasc_ecc,
                                      loc=mu_fasc_ecc,
                                      scale=std_fasc_ecc)
        fasc_eccs = fascEccDist.rvs(num_fascicle_attempt)

    if True in [fasc_ecc >= 1 for fasc_ecc in fasc_eccs]:
        raise Exception('A resulting eccentricity value exceeds 1. Eccentricity only defined in range [0,1).')

    # CALCULATE FASCICLE ROTATIONS
    fasc_rots = [360 * random.random() for _ in range(num_fascicle_attempt)]

    # CALCULATE FASCICLE MAJOR AND MINOR AXES
    a_axes = [((area ** 2) / ((np.pi ** 2) * (1 - (ecc ** 2)))) ** (1 / 4) for area, ecc in zip(fasc_areas, fasc_eccs)]
    b_axes = [area / (np.pi * a_axis) for area, a_axis in zip(fasc_areas, a_axes)]

    fascicles = []
    n_itr = []
    skipped_fascicles_index = []

    # DEFINE NERVE
    nerve = shapely.geometry.Point(0, 0).buffer(d_nerve / 2)

    # DEFINE/PLACE FASCICLES
    for i in range(num_fascicle_attempt):
        n_itr.append(0)

        while True:
            n_itr[i] += 1

            if n_itr[i] > max_attempt_iter:
                skipped_fascicles_index.append(i)
                break

            # https://gis.stackexchange.com/questions/243459/drawing-ellipse-with-shapely
            p = get_random_point_in_polygon(nerve)
            # 1st elem = center point (x,y) coordinates
            # 2nd elem = the two semi-axis values (along x, along y)
            # 3rd elem = angle in degrees between x-axis of the Cartesian base
            #            and the corresponding semi-axis
            ellipse = (p, (a_axes[i], b_axes[i]), fasc_rots[i])
            fascicle_attempt = shapely.geometry.Point(p).buffer(1)
            fascicle_attempt = shapely.affinity.scale(fascicle_attempt, ellipse[1][0], ellipse[1][1], 0, ellipse[0])
            fascicle_attempt = shapely.affinity.rotate(fascicle_attempt, fasc_rots[i], origin='center',
                                                       use_radians=False)

            chk = 0
            if fascicle_attempt.buffer(min_fascicle_separation).boundary.intersects(nerve.boundary):
                chk = 1

            if any([fasc.buffer(min_fascicle_separation).intersects(fascicle_attempt) for fasc in fascicles]):
                chk = 1

            if chk == 0:
                fascicles.append(fascicle_attempt)
                break

    # print to console any fascicle diameters that were skipped
    if len(fascicles) < num_fascicle_attempt:
        print('ATTENTION: Either re-run program or reduce #/size/separation distance fascicles')
        print(
            'User requested {} fascicles, but program could only place {}'.format(num_fascicle_attempt, len(fascicles)))

    mockConfig['num_fascicle_placed'] = len(fascicles)

    with open(os.path.join(project_path, sample_dir, 'mock.json'), "w") as handle:
        handle.write(json.dumps(mockConfig, indent=2))

    # set figure background to black (contents white by default in image segmentation code)
    plt.style.use('dark_background')

    # NERVE BINARY IMAGE
    nerveFig = plt.figure(1)
    nerveAxis = nerveFig.add_subplot(111)
    x, y = nerve.exterior.xy
    nerveAxis.fill(x, y, 'w')
    nerveAxis.set_aspect('equal')
    plt.axis('off')
    nerveAxis.set_xlim(fig_margin * -d_nerve / 2, fig_margin * d_nerve / 2)
    nerveAxis.set_ylim(fig_margin * -d_nerve / 2, fig_margin * d_nerve / 2)
    pngNerve = BytesIO()
    nerveFig.savefig(pngNerve, dpi=fig_dpi, format='png')
    pngNerve.seek(0)
    imgNerve = create_opencv_image_from_stringio(pngNerve)
    _, bw_img_nerve = cv2.threshold(imgNerve, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite(os.path.join(project_path, sample_dir, '{}_0_0_n.tif'.format(sample_str)), bw_img_nerve)

    # FASCICLES BINARY IMAGE
    fasciclesFig = plt.figure(2)
    fasciclesAxis = fasciclesFig.add_subplot(111)
    for fascicle in fascicles:
        if fascicle is not None and fascicle.exterior is not None:
            x, y = fascicle.exterior.xy
            fasciclesAxis.fill(x, y, 'w')

    fasciclesAxis.set_aspect('equal')
    plt.axis('off')
    fasciclesAxis.set_xlim(fig_margin * -d_nerve / 2, fig_margin * d_nerve / 2)
    fasciclesAxis.set_ylim(fig_margin * -d_nerve / 2, fig_margin * d_nerve / 2)
    pngFascicles = BytesIO()
    fasciclesFig.savefig(pngFascicles, dpi=fig_dpi, format='png')
    pngFascicles.seek(0)
    imgFascicles = create_opencv_image_from_stringio(pngFascicles)
    ret, bw_img_fascicles = cv2.threshold(imgFascicles, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite(os.path.join(project_path, sample_dir, '{}_0_0_i.tif'.format(sample_str)), bw_img_fascicles)

    # SCALEBAR BINARY IMAGE
    scalebarFig = plt.figure(3)
    scalebarAxis = scalebarFig.add_subplot(111)
    plt.plot([0, scalebar_length], [0, 0], '-w')
    scalebarAxis.set_aspect('equal')
    plt.axis('off')
    scalebarAxis.set_xlim(fig_margin * -d_nerve / 2, fig_margin * d_nerve / 2)
    scalebarAxis.set_ylim(fig_margin * -d_nerve / 2, fig_margin * d_nerve / 2)
    pngScaleBar = BytesIO()
    scalebarFig.savefig(pngScaleBar, dpi=fig_dpi, format='png')
    pngScaleBar.seek(0)
    imgScaleBar = create_opencv_image_from_stringio(pngScaleBar)
    _, bw_img_scalebar = cv2.threshold(imgScaleBar, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite(os.path.join(project_path, sample_dir, '{}_0_0_s.tif'.format(sample_str)), bw_img_scalebar)

elif method == "explicit":
    # DEFINE NERVE
    nerve = shapely.geometry.Point(0, 0).buffer(d_nerve / 2)

    fascicles = []
    fascs_explicit = mockConfig.get('explicit').get('Fascicles')

    fasc_centroid_xs = [0] * len(fascs_explicit)
    fasc_centroid_ys = [0] * len(fascs_explicit)
    fasc_as = [0] * len(fascs_explicit)
    fasc_bs = [0] * len(fascs_explicit)
    fasc_rots = [0] * len(fascs_explicit)

    for fasc_ind, fascicle in enumerate(fascs_explicit):
        fasc_centroid_xs[fasc_ind] = fascicle.get('centroid_x')
        fasc_centroid_ys[fasc_ind] = fascicle.get('centroid_y')
        fasc_as[fasc_ind] = fascicle.get('a')
        fasc_bs[fasc_ind] = fascicle.get('b')
        fasc_rots[fasc_ind] = fascicle.get('rot')

    for fasc_ind, fascicle in enumerate(fascs_explicit):
        p = (fasc_centroid_xs[fasc_ind], fasc_centroid_ys[fasc_ind])
        ellipse = (p,
                   (fasc_as[fasc_ind], fasc_bs[fasc_ind]),
                   fasc_rots[fasc_ind])

        fascicle_attempt = shapely.geometry.Point(p).buffer(1)
        fascicle_attempt = shapely.affinity.scale(fascicle_attempt, ellipse[1][0], ellipse[1][1], 0, ellipse[0])
        fascicle_attempt = shapely.affinity.rotate(fascicle_attempt, fasc_rots[fasc_ind], origin='center',
                                                   use_radians=False)

        chk = 0
        if fascicle_attempt.buffer(min_fascicle_separation).boundary.intersects(nerve.boundary):
            chk = 1

        if any([fasc.buffer(min_fascicle_separation).intersects(fascicle_attempt) for fasc in fascicles]):
            chk = 1

        if chk == 0:
            fascicles.append(fascicle_attempt)

    # print to console any fascicle diameters that were skipped
    if len(fascicles) < len(fascs_explicit):
        raise Exception('ATTENTION: Explicit fascicle positions do not satisfy parameter "min_fascicle_separation" '
                        'due to either fascicles being too close to each other or the nerve boundary.')

    # set figure background to black (contents white by default in image segmentation code)
    plt.style.use('dark_background')

    # NERVE BINARY IMAGE
    nerveFig = plt.figure(1)
    nerveAxis = nerveFig.add_subplot(111)
    x, y = nerve.exterior.xy
    nerveAxis.fill(x, y, 'w')
    nerveAxis.set_aspect('equal')
    plt.axis('off')
    nerveAxis.set_xlim(fig_margin * -d_nerve / 2, fig_margin * d_nerve / 2)
    nerveAxis.set_ylim(fig_margin * -d_nerve / 2, fig_margin * d_nerve / 2)
    pngNerve = BytesIO()
    nerveFig.savefig(pngNerve, dpi=fig_dpi, format='png')
    pngNerve.seek(0)
    imgNerve = create_opencv_image_from_stringio(pngNerve)
    _, bw_img_nerve = cv2.threshold(imgNerve, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite(os.path.join(project_path, sample_dir, '{}_0_0_n.tif'.format(sample_str)), bw_img_nerve)

    # FASCICLES BINARY IMAGE
    fasciclesFig = plt.figure(2)
    fasciclesAxis = fasciclesFig.add_subplot(111)
    for fascicle in fascicles:
        if fascicle is not None and fascicle.exterior is not None:
            x, y = fascicle.exterior.xy
            fasciclesAxis.fill(x, y, 'w')

    fasciclesAxis.set_aspect('equal')
    plt.axis('off')
    fasciclesAxis.set_xlim(fig_margin * -d_nerve / 2, fig_margin * d_nerve / 2)
    fasciclesAxis.set_ylim(fig_margin * -d_nerve / 2, fig_margin * d_nerve / 2)
    pngFascicles = BytesIO()
    fasciclesFig.savefig(pngFascicles, dpi=fig_dpi, format='png')
    pngFascicles.seek(0)
    imgFascicles = create_opencv_image_from_stringio(pngFascicles)
    ret, bw_img_fascicles = cv2.threshold(imgFascicles, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite(os.path.join(project_path, sample_dir, '{}_0_0_i.tif'.format(sample_str)), bw_img_fascicles)

    # SCALEBAR BINARY IMAGE
    scalebarFig = plt.figure(3)
    scalebarAxis = scalebarFig.add_subplot(111)
    plt.plot([0, scalebar_length], [0, 0], '-w')
    scalebarAxis.set_aspect('equal')
    plt.axis('off')
    scalebarAxis.set_xlim(fig_margin * -d_nerve / 2, fig_margin * d_nerve / 2)
    scalebarAxis.set_ylim(fig_margin * -d_nerve / 2, fig_margin * d_nerve / 2)
    pngScaleBar = BytesIO()
    scalebarFig.savefig(pngScaleBar, dpi=fig_dpi, format='png')
    pngScaleBar.seek(0)
    imgScaleBar = create_opencv_image_from_stringio(pngScaleBar)
    _, bw_img_scalebar = cv2.threshold(imgScaleBar, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite(os.path.join(project_path, sample_dir, '{}_0_0_s.tif'.format(sample_str)), bw_img_scalebar)






# N = stats.norm(loc=mu_fasc, scale=std_fasc)
# fig, ax = plt.subplots(2, sharex=True)
# ax[0].hist(X.rvs(10000), density=True)
# ax[1].hist(N.rvs(10000), density=True)
# plt.show

# END timer
end = time.time()
print('\nruntime: {}'.format(end - start))

# cleanup for console viewing/inspecting
del start, end
