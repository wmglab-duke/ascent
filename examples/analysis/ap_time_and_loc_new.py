#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import os
import sys

sys.path.append(os.path.sep.join([os.getcwd(), '']))
os.chdir('D:/ASCENT/fresh')
import numpy as np

import matplotlib.pyplot as plt
from src.core.query import Query

# set default fig size
plt.rcParams['figure.figsize'] = list(np.array([16.8, 10.14]) / 2)

q = Query({
    'partial_matches': False,
    'include_downstream': True,
    'indices': {
        'sample': [0],
        'model': [0],
        'sim': [9]
    }
}).run()

q.ap_loctime(
    plot=False,
    absolute_voltage=False,
    save=True,
    nodes_only = True,
    amp = 0)
