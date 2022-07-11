#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import os

import matplotlib.pyplot as plt
import numpy as np

sample = 3008
model = 6
sim = 3001

base_n_sim = os.path.join('samples', str(sample), 'models', str(model), 'sims', str(sim), 'n_sims')

inner = 0
fiber = 0
n_sims = list(range(6))  # [0, 4, 8, 12, 16, 20]
pve1 = os.path.join(
    base_n_sim,
    str(n_sims[0]),
    'data',
    'inputs',
    'inner{}_fiber{}.dat'.format(inner, fiber),
)
dpve1 = np.loadtxt(pve1)
plt.plot(dpve1[1:], 'r-', label='p1')

fiberset = 0
fiber = inner
base_fiberset = os.path.join(
    'samples',
    str(sample),
    'models',
    str(model),
    'sims',
    str(sim),
    'potentials',
    str(fiberset),
)
fve1 = os.path.join(base_fiberset, '{}.dat'.format(fiber))
dfve1 = np.loadtxt(fve1)
plt.plot(dfve1[1:], 'g--', label='f1')
plt.legend()
plt.show()

print('done')
