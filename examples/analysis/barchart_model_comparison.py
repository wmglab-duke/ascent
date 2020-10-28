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
# q = Query({
#     'partial_matches': True,
#     'include_downstream': True,
#     'indices': {
#         'sample': [3],
#         'model': [0, 1, 2, 3],
#         'sim': [0]
#     }
# }).run()
#
# # builds heatmaps
# q.barcharts_compare_models(model_labels=['Original orientation',
#                                          '90-degree rotation',
#                                          '180-degree rotation',
#                                          '270-degree rotation'],
#                            title= 'Upper lobe activation thresholds',
#                            fascicle_filter_indices=[2, 3, 9, 7, 13, 15, 4, 0, 6, 10, 15, 18, 16, 1, 11, 17, 5, 8, 14, 12, 21, 23, 20, 25, 32],
#                            logscale=True)

q = Query({
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'samples': [1017],
        'model': [4, 5, 6, 7],
        'sim': [1040]
    }
}).run()

# builds heatmaps
q.barcharts_compare_models(logscale=False,
                           model_labels=['Model 0: Veltink Epineurium, \n              Veltink Perineurium',
                                         'Model 1: Veltink Epineurium, \n              Goodall Perineurium',
                                         'Model 2: Goodall Epineurium, \n              Veltink Perineurium',
                                         'Model 3: Goodall Epineurium, \n              Goodall Perineurium']
                           )