#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

from matplotlib import pyplot as plt
import matplotlib
import numpy as np
import os
import matplotlib.backend_tools as bt

print(os.getcwd())

n_sim_base = 'out/submit/n_sims/3008'
sim = '3001'
models = range(12)
fibers = range(6)
threshold = '/data/outputs/thresh_inner0_fiber0.dat'

baseline_model = 10

radii = [7500, 7500, 7500, 10000, 10000, 10000, 12500, 12500, 12500, 15000, 15000, 15000]
hmaxes = [800, 1600, 3200] * 4
hmins = [5, 10, 20] * 4
diams = ['1', '2', '5.7', '7.3', '8.7', '10']

baseline_results = []
model_results = []

for model in models:
    fiber_results = []
    for fiber in fibers:
        value = np.loadtxt('_'.join([n_sim_base, str(model), sim, str(fiber) + threshold])).tolist()
        fiber_results.append(value)
        if model == baseline_model:
            baseline_results.append(value)
    model_results.append(fiber_results)

fig, axs = plt.subplots(4, 3)
for i, (ax, model, radius, hmax, hmin) in enumerate(zip(axs.flatten(), model_results, radii, hmaxes, hmins)):
    print(f'MODEL {model}: {radius} {hmax} {hmin}')
    results = []
    for my_fiber, baseline_fiber in zip(model, baseline_results):
        results.append(round(100 * (my_fiber - baseline_fiber) / baseline_fiber, 2))
    ax.set_title(f'Radius: {radius}µm\nMax mesh element size: {hmax} µm, Min mesh element size: {hmin} µm')
    ax.title.set_size(7)
    if i != baseline_model:
        ax.bar(fibers, results, 0.5)
        ax.set_xticks(fibers)
        ax.set_xticklabels(diams)
        ax.set_xlabel('MRG Fiber Diameter, µm', fontsize=7)
    else:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.text(0.5, 0.5, 'BASELINE', horizontalAlignment='center', verticalAlignment='center', fontsize=15)
plt.suptitle('SL Activation Threshold Percent Error from \"Baseline\" Model')
plt.subplots_adjust(hspace=0.75)
plt.show()
