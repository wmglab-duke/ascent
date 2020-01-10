from copy import deepcopy
import random

import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np

d_nerve = 400
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
			tmp = np.sqrt((x_fasc[i]-x_fasc[fasc_comp])**2 + (y_fasc[i]-y_fasc[fasc_comp])**2)
			min_dist = min_fascicle_separation + (fasc_diameters[i] + fasc_diameters[fasc_comp])/2

			if tmp < min_dist:
				chk = 1  # too close
				break

		if chk == 0:
			break

print("fasc_diameters")
print(fasc_diameters)
print("d_fasc_skipped")
print(d_fasc_skipped)

fasc_diameters_post = [f for f, d in zip(fasc_diameters, d_fasc_skipped) if abs(f - d) > 0.001]
x_fasc = [x for x, f, d in zip(x_fasc, fasc_diameters, d_fasc_skipped) if abs(f - d) > 0.001]
y_fasc = [y for y, f, d in zip(y_fasc, fasc_diameters, d_fasc_skipped) if abs(f - d) > 0.001]

print("fasc_diameters_post")
print(fasc_diameters_post)
print(x_fasc)
print(y_fasc)


fig, ax = plt.subplots()
# Plot Nerve
nerve = plt.Circle((0, 0), d_nerve/2, color='b')
ax.add_artist(nerve)

plt.plot(x_fasc, y_fasc, 'ro')

plt.plot(x_fasc, y_fasc, 'ro')

for fasc in range(len(fasc_diameters_post)):
	print(fasc)
	fascPlot = plt.Circle((x_fasc[fasc], y_fasc[fasc]), fasc_diameters_post[fasc]/2, color='r')
	ax.add_artist(fascPlot)

ax.set_aspect('equal', 'box')
plt.ylim(ymax=d_nerve/2, ymin=-d_nerve/2)
plt.xlim(xmax=d_nerve/2, xmin=-d_nerve/2)

plt.show()

# N = stats.norm(loc=mu_fasc, scale=std_fasc)
# fig, ax = plt.subplots(2, sharex=True)
# ax[0].hist(X.rvs(10000), density=True)
# ax[1].hist(N.rvs(10000), density=True)
# plt.show()
