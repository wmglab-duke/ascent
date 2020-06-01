import os
import numpy as np
import matplotlib.pyplot as plt

sample = 80
model = 0
sim = 10

base = os.path.join('..', '..', 'samples', str(sample), 'models', str(model), 'sims', str(sim), 'n_sims')

n_sims = [0, 4, 8, 12, 16, 20]
inner = 0
fiber = 0

pve1 = os.path.join(base, str(n_sims[0]), 'data', 'inputs', 'inner{}_fiber{}.dat'.format(inner, fiber))

os.path.exists(pve1)

pve2 = os.path.join(base, str(n_sims[1]), 'data', 'inputs', 'inner{}_fiber{}.dat'.format(inner, fiber))
pve3 = os.path.join(base, str(n_sims[2]), 'data', 'inputs', 'inner{}_fiber{}.dat'.format(inner, fiber))
pve4 = os.path.join(base, str(n_sims[3]), 'data', 'inputs', 'inner{}_fiber{}.dat'.format(inner, fiber))
pve5 = os.path.join(base, str(n_sims[4]), 'data', 'inputs', 'inner{}_fiber{}.dat'.format(inner, fiber))
pve6 = os.path.join(base, str(n_sims[5]), 'data', 'inputs', 'inner{}_fiber{}.dat'.format(inner, fiber))

ve1 = np.loadtxt(pve1)
plt.plot(ve1[1:])
plt.show()



print('done')
