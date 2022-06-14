#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent

Plots the voltage along a fiber, as well as its first and second spatial differential.
Note: Run from repository root
"""

import os
import numpy as np
import matplotlib.pyplot as plt

sample = 1000
model = 0
sim = 0
inner = 0
fiber = 0
n_sim = 0

myelinated = True

#%% Plot Ve graphs
base_n_sim = os.path.join('samples', str(sample), 'models', str(model), 'sims', str(sim), 'n_sims')

plt.figure()
pve1 = os.path.join(base_n_sim, str(n_sim), 'data', 'inputs', 'inner{}_fiber{}.dat'.format(inner, fiber))
dpve1 = np.loadtxt(pve1)
if myelinated: dpve1 = [dpve1[i] for i in range(len(dpve1)) if i % 11 == 0]
plt.plot(dpve1[1:], 'r-', label='p1')
plt.title('Ve')
plt.show()

plt.figure()
der1 = [dpve1[i+1]-dpve1[i] for i in range(len(dpve1)-1)]
plt.plot(der1[1:], 'r-', label='p1')
plt.title('Ve 1st differential')
plt.show()

plt.figure()
der2 = [der1[i+1]-der1[i] for i in range(len(der1)-1)]
plt.plot(der2[1:], 'r-', label='p1')
plt.title('Ve 2nd differential')
plt.show()

