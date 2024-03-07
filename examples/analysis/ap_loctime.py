"""Plots the time and location where an action potential occurred.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent.

This script requires that the user set saving aploctime to true in sim.json.
RUN THIS FROM REPOSITORY ROOT
"""

import os
import sys

sys.path.append(os.path.sep.join([os.getcwd(), '']))

import matplotlib.pyplot as plt
import numpy as np

from src.core.plotter import ap_loctime
from src.core.query import Query

# set default fig size
plt.rcParams['figure.figsize'] = list(np.array([16.8, 10.14]) / 2)

q = Query(
    {'partial_matches': False, 'include_downstream': True, 'indices': {'sample': [0], 'model': [0], 'sim': [0]}}
).run()

ap_loctime(q, plot=True, plot_distribution=False, save=False, nodes_only=True, amp=0)
