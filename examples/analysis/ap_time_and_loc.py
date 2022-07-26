#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent

This script plots action potential time and location along fibers, as well as plotting Ve along the fiber.
This requires that you have saved Vm at all locs (under time).
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np

from src.core.query import Query

sys.path.append(os.path.sep.join([os.getcwd(), '']))

# set default fig size
plt.rcParams['figure.figsize'] = list(np.array([16.8, 10.14 * 2]) / 2)

q = Query(
    {
        'partial_matches': False,
        'include_downstream': True,
        'indices': {'sample': [3008], 'model': [0, 1, 2, 11], 'sim': [3001]},
    }
).run()

q.ap_time_and_location(
    delta_V=60,
    plot=False,
    absolute_voltage=False,
    save=True,
    subplots=True,
    nodes_only=True,
)
