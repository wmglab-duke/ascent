#!/usr/bin/env python3.7

# RUN THIS FROM REPOSITORY ROOT

import os
import sys

sys.path.append(os.path.sep.join([os.getcwd(), '']))

import numpy as np

import matplotlib.pyplot as plt
from src.core.query import Query

# set default fig size
plt.rcParams['figure.figsize'] = list(np.array([16.8, 10.14]) / 2)

# initialize and run Querys
q = Query({
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'sample': [3],
        'model': [0, 1, 2, 3],
        'sim': [0]
    }
}).run()

# builds heatmaps
q.barcharts_compare_models(model_labels=['Original orientation',
                                         '90-degree rotation',
                                         '180-degree rotation',
                                         '270-degree rotation'],
                           fascicle_filter_indices=[8],
                           logscale=True)
