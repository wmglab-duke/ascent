from copy import deepcopy

import random
from io import BytesIO

import scipy.stats as stats
import numpy as np
from PIL import Image

from shapely.geometry.point import Point
import shapely.affinity

import matplotlib.pyplot as plt

# choose fascicle area


d_nerve = 400

mu_fasc_area = 3000
std_fasc_area = 1500

mu_fasc_ecc = 0.4
std_fasc_ecc = 0.2

num_fascicle = 15

n_std_area_limit = 2
n_std_ecc_limit = 2

min_fascicle_separation = 5
max_iter = 1000

min_eccentricity = 0  # circle
max_eccentricity = 0.7  # most extreme ellipse

# AREA
lower_fasc_area, upper_fasc_area = mu_fasc_area - n_std_area_limit * std_fasc_area, \
             mu_fasc_area + n_std_area_limit * std_fasc_area

fascAreaDist = stats.truncnorm((lower_fasc_area - mu_fasc_area) / std_fasc_area,
                    (upper_fasc_area - mu_fasc_area) / std_fasc_area,
                    loc=mu_fasc_area,
                    scale=std_fasc_area)

fasc_areas = np.sort(fascAreaDist.rvs(num_fascicle))[::-1].T

# ECCENTRICITY
lower_fasc_ecc, upper_fasc_ecc = mu_fasc_ecc - n_std_ecc_limit * std_fasc_ecc, \
                                   mu_fasc_ecc + n_std_ecc_limit * std_fasc_ecc

fascEccDist = stats.truncnorm((lower_fasc_ecc - mu_fasc_ecc) / std_fasc_ecc,
                               (upper_fasc_ecc - mu_fasc_ecc) / std_fasc_ecc,
                               loc=mu_fasc_ecc,
                               scale=std_fasc_ecc)

fasc_eccs = fascEccDist.rvs(num_fascicle)

# ROTATIONS
fasc_rots = [360*random.random() for _ in range(num_fascicle)]

# MAJOR AND MINOR AXES
a_axes = [((area**2)/((np.pi**2)*(1-(ecc**2))))**(1/4) for area, ecc in zip(fasc_areas, fasc_eccs)]
b_axes = [area/(np.pi*a_axis) for area, a_axis in zip(fasc_areas, a_axes)]

fascicles = []
n_itr = []
skipped_fascicles = []
nerve = shapely.geometry.Point(0, 0).buffer(d_nerve/2)

def get_random_point_in_polygon(poly):
    minx, miny, maxx, maxy = poly.bounds
    while True:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if poly.contains(p):
            return p


for i in range(num_fascicle):
    n_itr.append(0)

    while True:
        n_itr[i] += 1

        if n_itr[i] > max_iter:
            skipped_fascicles.append(i)
            print('skipped fascicle{}'.format(i))
            break

        p = get_random_point_in_polygon(nerve)
        # 1st elem = center point (x,y) coordinates
        # 2nd elem = the two semi-axis values (along x, along y)
        # 3rd elem = angle in degrees between x-axis of the Cartesian base
        #            and the corresponding semi-axis
        ellipse = (p, (a_axes[i], b_axes[i]), fasc_rots[i])
        fascicle_attempt = shapely.geometry.Point(p).buffer(1)
        fascicle_attempt = shapely.affinity.scale(fascicle_attempt, ellipse[1][0], ellipse[1][1], 0, ellipse[0])
        fascicle_attempt = shapely.affinity.rotate(fascicle_attempt, fasc_rots[i], origin='center', use_radians=False)

        chk = 0
        if fascicle_attempt.buffer(min_fascicle_separation).boundary.intersects(nerve.boundary):
            chk = 1

        if any([fasc.buffer(min_fascicle_separation).intersects(fascicle_attempt) for fasc in fascicles]):
            chk = 1

        if chk == 0:
            fascicles.append(fascicle_attempt)
            break

# aliasing, binary?
plt.style.use('dark_background')
fig = plt.figure()
ax = plt.subplot(1, 1, 1)
x, y = nerve.exterior.xy
plt.fill(x, y, 'w')
ax.set_aspect('equal', 'box')
plt.axis('off')

plt.figure(2)
ax2 = plt.subplot(1, 1, 1)
for fascicle in fascicles:
    if fascicle is not None and fascicle.exterior is not None:
        x, y = fascicle.exterior.xy
        plt.fill(x, y, 'w')

ax2.set_aspect('equal', 'box')
plt.axis('off')


#
# print('skipped_fascicles: '.format(skipped_fascicles))
# fig_margin = 1.2
# ax.set_aspect('equal', 'box')
# plt.ylim(ymax=fig_margin*d_nerve / 2, ymin=fig_margin*-d_nerve / 2)
# plt.xlim(xmax=fig_margin*d_nerve / 2, xmin=fig_margin*-d_nerve / 2)
# plt.axis('off')


# N = stats.norm(loc=mu_fasc, scale=std_fasc)
# fig, ax = plt.subplots(2, sharex=True)
# ax[0].hist(X.rvs(10000), density=True)
# ax[1].hist(N.rvs(10000), density=True)
# plt.show()


# https://stackoverflow.com/questions/37945495/save-matplotlib-figure-as-tiff
# save figure
# (1) save the image in memory in PNG format



png1 = BytesIO()
fig.savefig(png1, format='png')

# (2) load this image into PIL
png2 = Image.open(png1)

# (3) save as TIFF
png2.save('Test.png', qtables=png2.quantization)
png1.close()
