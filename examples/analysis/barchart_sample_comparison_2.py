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
        'sample': [0],
        'model': [0],
        'sim': [1]
    }
}).run()

# builds heatmaps
q.barcharts_compare_samples_2(model_labels=['0'],
                              sample_labels=['LivaNova'],
                              title='SL Activation Thresholds')
