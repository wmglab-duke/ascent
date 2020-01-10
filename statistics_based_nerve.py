from copy import deepcopy
import random

import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np

d_nerve = 200
mu_fasc = 100
std_fasc = 30
num_fascicle = 15
n_std_limit = 2
min_fascicle_separation = 10
max_iter = 1000

lower, upper \
	= mu_fasc - n_std_limit * std_fasc, mu_fasc + n_std_limit * std_fasc

X = stats.truncnorm((lower - mu_fasc) / std_fasc,
					(upper - mu_fasc) / std_fasc,
					loc=mu_fasc,
					scale=std_fasc)

fasc_diameters = np.sort(X.rvs(num_fascicle))

r = np.zeros(np.size(fasc_diameters))
theta = deepcopy(r)
x_fasc = deepcopy(r)
y_fasc = deepcopy(r)
n_itr = deepcopy(r)
d_fasc_skipped = deepcopy(r)

for i in range(num_fascicle):
	while 1:
		n_itr[i] += 1

		if n_itr[i] > max_iter:
			d_fasc_skipped[i] = fasc_diameters[i]
			break

		theta[i] = 2 * np.pi * random.random()
		r[i] = (d_nerve/2 - fasc_diameters[i]/2 - min_fascicle_separation) * np.sqrt(random.random())
		x_fasc[i] = r[i]*np.cos(theta[i])
		y_fasc[i] = r[i]*np.sin(theta[i])

		chk = 0
		for fasc_comp in range(0, i-1):
			tmp = np.sqrt(x_fasc[i]-x_fasc[fasc_comp])**2 + np.sqrt(y_fasc[i]-y_fasc[fasc_comp])**2
			min_dist = min_fascicle_separation + (fasc_diameters[i] + fasc_diameters[fasc_comp])/2

			if tmp < min_dist:
				chk = 1  # too close
				break

		if chk == 0:
			break

fasc_diameters = fasc_diameters[fasc_diameters != d_fasc_skipped]
x_fasc = x_fasc[fasc_diameters != d_fasc_skipped]
y_fasc = y_fasc[fasc_diameters != d_fasc_skipped]





# N = stats.norm(loc=mu_fasc, scale=std_fasc)

# fig, ax = plt.subplots(2, sharex=True)
# ax[0].hist(X.rvs(10000), density=True)
# ax[1].hist(N.rvs(10000), density=True)
# plt.show()
