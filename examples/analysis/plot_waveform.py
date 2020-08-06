#!/usr/bin/env python3.7

import os
import sys
import json

root = os.path.abspath(os.path.join(*'../../'.split('/')))
sys.path.append(root)

from src.core import Simulation
from src.core import Waveform
from src.core.query import Query
from src.utils import *
import matplotlib.pyplot as plt


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
    'indices': {
        'sample': [1000],
        'model': [0],
        'sim': [1000]
    }
}

q = Query(criteria)
q.run()

results = q.summary()

sample_index = results['samples'][0]['index']
model_index = results['samples'][0]['models'][0]['index']
sim_index = 1000

item: Simulation = q.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])
waveform: Waveform = item.waveforms[0]

fig, ax = plt.subplots(1, 1)
waveform.plot(ax=ax)
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude (unscaled)')
plt.show()

fname = 'my_waveform'
fmt = 'png'

dest = os.path.join('data', 'tmp')
if not os.path.exists(dest):
    os.mkdir(dest)

fig.savefig(os.path.join(dest, '{}.{}'.format(fname, fmt)), format=fmt, dpi=1200)

os.chdir(cwd)
