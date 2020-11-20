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


# M10
# # initialize and run Querys
# qMRG = Query({
#     'partial_matches': True,
#     'include_downstream': True,
#     'indices': {
#         'sample': [62, 63, 64, 65, 66, 67, 68, 69, 70],
#         'model': [0, 2, 3],
#         'sim': [0]
#     }
# }).run()
#
# axMRG = qMRG.barcharts_compare_samples(merge_bars=True, calculation='i50')
#
# qC = Query({
#     'partial_matches': True,
#     'include_downstream': True,
#     'indices': {
#         'sample': [62, 63, 64, 65, 66, 67, 68, 69, 70],
#         'model': [0, 2, 3],
#         'sim': [2]
#     }
# }).run()
#
# axC = qC.barcharts_compare_samples(merge_bars=True, calculation='i50')

# initialize and run Querys
# qMRG = Query({
#     'partial_matches': True,
#     'include_downstream': True,
#     'indices': {
#         'sample': [71, 72, 73, 74, 75, 76, 77, 78, 79],  # add 71, 74
#         'model': [0, 1, 2],
#         'sim': [1]
#     }
# }).run()
#
# axMRG = qMRG.barcharts_compare_samples(merge_bars=True, calculation='i50')
#
# qC = Query({
#     'partial_matches': True,
#     'include_downstream': True,
#     'indices': {
#         'sample': [71, 72, 73, 74, 75, 76, 77, 78, 79],  # add 71, 74
#         'model': [0, 1, 2],
#         'sim': [3]
#     }
# }).run()
#axC = qC.barcharts_compare_samples(merge_bars=True, calculation='i50')

# _-Madison Pig
qMonoPolar = Query({
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'sample': [80],  # add 71, 74
        'model': [0],
        'sim': [10]
    }
}).run()

axMonoPolar = qMonoPolar.barcharts_compare_samples(merge_bars=True, calculation='i50')

print('done')
