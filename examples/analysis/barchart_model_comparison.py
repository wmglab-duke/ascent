#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

# RUN THIS FROM REPOSITORY ROOT

import os
import sys

import matplotlib.pyplot as plt
import numpy as np

from src.core.query import Query

sys.path.append(os.path.sep.join([os.getcwd(), '']))

# set default fig size
plt.rcParams['figure.figsize'] = list(np.array([16.8, 10.14]) / 2)

q = Query(
    {
        'partial_matches': False,
        'include_downstream': True,
        'indices': {'sample': [3008], 'model': [0, 1, 2], 'sim': [3001]},
    }
).run()

q.barcharts_compare_models(save_path='out/analysis')
