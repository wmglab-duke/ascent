from copy import deepcopy

import random
import scipy.stats as stats
import numpy as np

from shapely.geometry.point import Point
import shapely.affinity

import matplotlib.pyplot as plt


d_nerve = 400
mu_fasc = 50
std_fasc = 10
num_fascicle = 25
n_std_limit = 2
min_fascicle_separation = 5
max_iter = 1000

lower, upper = mu_fasc - n_std_limit * std_fasc, mu_fasc + n_std_limit * std_fasc

X = stats.truncnorm((lower - mu_fasc) / std_fasc,
                    (upper - mu_fasc) / std_fasc,
                    loc=mu_fasc,
                    scale=std_fasc)

fasc_diameters = np.sort(X.rvs(num_fascicle))[::-1]

fascicles = []
n_itr = []
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
            print('skipped fascicle{}'.format(i))
            break

        p = get_random_point_in_polygon(nerve)
        fascicle_attempt = shapely.geometry.Point(p).buffer(fasc_diameters[i]/2)

        chk = 0
        if fascicle_attempt.buffer(min_fascicle_separation).boundary.intersects(nerve.boundary):
            chk = 1

        if any([fasc.buffer(min_fascicle_separation).intersects(fascicle_attempt) for fasc in fascicles]):
            chk = 1

        if chk == 0:
            fascicles.append(fascicle_attempt)
            break

fig, ax = plt.subplots()
x, y = nerve.exterior.xy
plt.plot(x, y)

for fascicle in fascicles:
    if fascicle is not None and fascicle.exterior is not None:
        x, y = fascicle.exterior.xy
        plt.plot(x, y)

ax.set_aspect('equal', 'box')
plt.ylim(ymax=d_nerve / 2, ymin=-d_nerve / 2)
plt.xlim(xmax=d_nerve / 2, xmin=-d_nerve / 2)

plt.show()

# N = stats.norm(loc=mu_fasc, scale=std_fasc)
# fig, ax = plt.subplots(2, sharex=True)
# ax[0].hist(X.rvs(10000), density=True)
# ax[1].hist(N.rvs(10000), density=True)
# plt.show()
