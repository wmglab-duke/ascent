#!/usr/bin/env python3.7

"""Plot the waveform used for stimulation.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent.

RUN THIS FROM REPOSITORY ROOT
"""

import json
import os

import matplotlib.pyplot as plt

from src.core import Simulation
from src.core.query import Query
from src.utils import Object


def load(config_path: str):
    """Load in json data and returns to user, assuming it has already been validated.

    :param config_path: the string path to load up
    :return: json data (usually dict or list)
    """
    with open(config_path, "r") as handle:
        return json.load(handle)


criteria = {
    'partial_matches': True,
    'include_downstream': True,
    'indices': {'sample': [0], 'model': [0], 'sim': [0]},
}

q = Query(criteria)
q.run()

results = q.summary()

sample_index = results['samples'][0]['index']
model_index = results['samples'][0]['models'][0]['index']
sim_index = results['samples'][0]['models'][0]['sims'][0]

sim: Simulation = q.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

for waveform_ind, waveform in enumerate(sim.waveforms):
    waveform.plot()
    plt.xlabel('Time (ms)')
    plt.ylabel('Amplitude (unscaled)')

    fname = f'{str(sample_index)}_{str(model_index)}_{str(sim_index)}_{str(waveform_ind)}'
    fmt = 'png'

    dest = os.path.join('data', 'tmp', 'waveforms')
    if not os.path.exists(dest):
        os.mkdir(dest)

    plt.gcf().savefig(os.path.join(dest, f'{fname}.{fmt}'), format=fmt, dpi=1200)
