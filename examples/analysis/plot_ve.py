#!/usr/bin/env python3.7

"""Plot the Ve across a fiber length.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent.

RUN THIS FROM REPOSITORY ROOT
"""

import os

import matplotlib.pyplot as plt
import numpy as np

from src.core.query import Query
from src.utils import Object

sample = 0
model = 0
sim = 0
n_sim = 0
inner = 0
fiber = 0


base_n_sim = os.path.join('samples', str(sample), 'models', str(model), 'sims', str(sim), 'n_sims')

# load potentials, which are inputs to the n_sim
pve1 = os.path.join(base_n_sim, str(n_sim), 'data', 'inputs', f'inner{inner}_fiber{fiber}.dat')
dpve1 = np.loadtxt(pve1)

# load the corresponding fiber coordinates
sim_object = Query.get_object(Object.SIMULATION, [sample, model, sim])
for t, (p_i, _) in enumerate(sim_object.master_product_indices):
    if t == n_sim:
        potentials_ind = p_i
        break

active_src_ind, fiberset_ind = sim_object.potentials_product[potentials_ind]
master_fiber_ind = sim_object.indices_n_to_fib(fiberset_index=fiberset_ind, inner_index=inner, local_fiber_index=fiber)

fiber_coords_path = os.path.join(
    'samples',
    str(sample),
    'models',
    str(model),
    'sims',
    str(sim),
    'fibersets',
    str(fiberset_ind),
    f'{master_fiber_ind}.dat',
)
z_coords = np.loadtxt(fiber_coords_path, skiprows=1)[:, 2]

plt.plot(z_coords, dpve1[1:], 'r-', label='p1')
plt.ylabel('Ve (V)')
plt.xlabel('z-coordinates (\u03bcm)')

plt.legend()
plt.show()

print('done')
