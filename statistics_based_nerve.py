from scipy.stats import truncnorm
import matplotlib.pyplot as plt
import numpy as np

nerve_diameter = 2000
mean_fascicle_diameter = 100
std_fascicle_diameter = 30
num_fascicle = 5

a, b = (myclip_a - mean_fascicle_diameter) / std_fascicle_diameter, \
       (myclip_b - mean_fascicle_diameter) / std_fascicle_diameter

fig, ax = plt.subplots(1, 1)
mean, var, skew, kurt = truncnorm.stats(a, b, moments='mvsk')

x = np.linspace(truncnorm.ppf(0.01, a, b),truncnorm.ppf(0.99, a, b), 100)
ax.plot(x, truncnorm.pdf(x, a, b), 'r-', lw=5, alpha=0.6, label='truncnorm pdf')
ax.legend(loc='best', frameon=False)
plt.show()
