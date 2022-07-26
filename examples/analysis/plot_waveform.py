#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent

Plot the waveform used for stimulation.
"""

import json
import os
import sys

import matplotlib.pyplot as plt

from src.core import Simulation
from src.core.query import Query
from src.utils import Object

root = os.path.abspath(os.path.join('..', '..'))
sys.path.append(root)


def load(config_path: str):
    """
    Loads in json data and returns to user, assuming it has already been validated.
    :param config_path: the string path to load up
    :return: json data (usually dict or list)
    """
    with open(config_path, "r") as handle:
        return json.load(handle)


cwd = os.getcwd()
os.chdir(root)

criteria = {
    'partial_matches': True,
    'include_downstream': True,
    'indices': {'sample': [1000], 'model': [0], 'sim': [1000]},
}

q = Query(criteria)
q.run()

results = q.summary()

sample_index = results['samples'][0]['index']
model_index = results['samples'][0]['models'][0]['index']
sim_index = results['samples'][0]['models'][0]['sims'][0]

sim: Simulation = q.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

for waveform_ind, waveform in enumerate(sim.waveforms):
    fig, ax = plt.subplots(1, 1)
    waveform.plot(ax=ax)
    plt.xlabel('Time (ms)')
    plt.ylabel('Amplitude (unscaled)')
    plt.show()

    fname = '{}_{}_{}_{}'.format(str(sample_index), str(model_index), str(sim_index), str(waveform_ind))
    fmt = 'png'

    dest = os.path.join('data', 'tmp', 'waveforms')
    if not os.path.exists(dest):
        os.mkdir(dest)

    fig.savefig(os.path.join(dest, '{}.{}'.format(fname, fmt)), format=fmt, dpi=1200)

os.chdir(cwd)
