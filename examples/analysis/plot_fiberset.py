#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import os
import sys

root = os.path.abspath(os.path.join(*'../../'.split('/')))
sys.path.append(root)

from src.core import Simulation
from src.core import Sample
from src.core.query import Query
from src.utils import Object
import matplotlib.pyplot as plt

cwd = os.getcwd()
os.chdir(root)

criteria = {
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'sample': [1016],
        'model': [7],
        'sim': [1042]
    }
}


q = Query(criteria)
q.run()

results = q.summary()

sample_index = results['samples'][0]['index']
model_index = results['samples'][0]['models'][0]['index']
sim_index = results['samples'][0]['models'][0]['sims'][0]

sample: Sample = q.get_object(Object.SAMPLE, [results['samples'][0]['index']])
sim: Simulation = q.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

for fiberset_ind, fiberset in enumerate(sim.fibersets):
    slide = sample.slides[0]
    fig, ax = plt.subplots(1, 1)
    slide.plot(fix_aspect_ratio=True, final=False, ax=ax)

    for fiber in fiberset.fibers:
        plt.plot(fiber[0][0], fiber[0][1], 'r*', markersize=0.1)

    plt.xlabel('\u03bcm')
    plt.ylabel('\u03bcm')
    plt.show()

    fname = '{}_{}_{}_{}'.format(str(sample_index),
                                 str(model_index),
                                 str(sim_index),
                                 str(fiberset_ind))
    fmt = 'png'

    dest = os.path.join('data', 'tmp', 'fiberset')
    if not os.path.exists(dest):
        os.mkdir(dest)

    fig.savefig(os.path.join(dest, '{}.{}'.format(fname, fmt)), format=fmt, dpi=1200)

os.chdir(cwd)
