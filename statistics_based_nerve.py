#!/usr/bin/env python3.7

from copy import deepcopy
import random

import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np
from shapely.geometry.point import Point
import shapely.affinity

# https://gis.stackexchange.com/questions/243459/drawing-ellipse-with-shapely

d_nerve = 400
mu_fasc = 120
std_fasc = 30
num_fascicle = 3
n_std_limit = 2
min_fascicle_separation = 10
max_iter = 1000

lower, upper = mu_fasc - n_std_limit * std_fasc, mu_fasc + n_std_limit * std_fasc

X = stats.truncnorm((lower - mu_fasc) / std_fasc,
                    (upper - mu_fasc) / std_fasc,
                    loc=mu_fasc,
                    scale=std_fasc)

fasc_diameters = np.sort(X.rvs(num_fascicle))[::-1]
r = np.zeros(np.size(fasc_diameters))
d_fasc_skipped = deepcopy(r)

fascicles = []
n_itr = []
nerve = shapely.geometry.Point(0, 0).buffer(d_nerve / 2)


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
        print(n_itr[i])

        if n_itr[i] > max_iter:
            d_fasc_skipped[i] = fasc_diameters[i]
            break

        p = get_random_point_in_polygon(nerve)
        fascicle_attempt = shapely.geometry.Point(p).buffer(fasc_diameters[i]/2)

        chk = 0

        if fascicle_attempt.intersects(nerve):
            print('nerve intersects')
            chk = 1
            break

        for fasc_comp in range(0, i - 1):
            print('fascicle intersects')

            if fascicles[fasc_comp].boundary.intersects(fascicle_attempt.boundary):
                print('intersects')
                chk = 1
                break

        if chk == 0:
            print('appending')
            fascicles.append(fascicle_attempt)
            break

fasc_diameters_post = [f for f, d in zip(fasc_diameters, d_fasc_skipped) if abs(f - d) > 0.001]

fig, ax = plt.subplots()
# Plot Nerve
# nerve = plt.Circle((0, 0), d_nerve / 2, color='b')
# plt.plot(x_fasc, y_fasc, 'ro')
# plt.plot(x_fasc, y_fasc, 'ro')

x, y = nerve.exterior.xy
plt.plot(x, y)

for fascicle in fascicles:
    x, y = fascicle.exterior.xy
    plt.plot(x, y)

ax.set_aspect('equal', 'box')
plt.ylim(ymax=d_nerve / 2, ymin=-d_nerve / 2)
plt.xlim(xmax=d_nerve / 2, xmin=-d_nerve / 2)

plt.show()

#

# N = stats.norm(loc=mu_fasc, scale=std_fasc)
# fig, ax = plt.subplots(2, sharex=True)
# ax[0].hist(X.rvs(10000), density=True)
# ax[1].hist(N.rvs(10000), density=True)
# plt.show()
