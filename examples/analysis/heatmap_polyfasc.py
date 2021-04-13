#!/usr/bin/env python3.7

# RUN THIS FROM REPOSITORY ROOT

# ASSUMPTIONS: (old, moved to Query.heatmaps)
#   1) 1:1 inner:outer for all fascicles
#   2) Single slide for each sample (0_0)
#   3) Single fiber per inner
# TODO: Change above assumptions in later iteration? (highest priority is probably assumption 3)

import os
import sys

sys.path.append(os.path.sep.join([os.getcwd(), '']))

import matplotlib.pyplot as plt
from src.core.query import Query

# set default fig size
plt.rcParams['figure.figsize'] = [16.8/3, 10.14*2 * 0.9]

# initialize and run Querys
q = Query({
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'sample': [3006, 3007],
        'model': [0, 1, 2, 3],
        'sim': [3000]
    }
}).run()

# NOTE: these values were copied from the output of heatmaps(), setting the track_colormap_bounds flag True
colormap_bounds_override = None
# colormap_bounds_override = [
#     [
#         (0.322187, 1.51728),
#         (0.110607, 0.64657),
#         (0.03439, 0.133777),
#         (0.026082, 0.091096),
#         (0.023491, 0.077376),
#         (0.020899, 0.06945),
#     ],
#     [
#         (0.568523, 1.4246),
#         (0.177679, 0.624619),
#         (0.049023, 0.161826),
#         (0.036371, 0.115485),
#         (0.031646, 0.099632),
#         (0.027606, 0.089571),
#     ],
#     [
#         (0.658765, 1.619717),
#         (0.206337, 0.727056),
#         (0.059389, 0.19963),
#         (0.044908, 0.15024),
#         (0.039725, 0.131948),
#         (0.034542, 0.118534),
#     ],
#     [
#         (0.946562, 1.4246),
#         (0.280725, 0.62218),
#         (0.068535, 0.152679),
#         (0.048566, 0.107559),
#         (0.040335, 0.092315),
#         (0.035304, 0.082864),
#     ]
# ]

# colormap_bounds_override = [
#     [
#         (0.35440570000000005, 1.365552),
#         (0.1216677, 0.581913),
#         (0.037829, 0.12039930000000001),
#         (0.028690200000000003, 0.0819864),
#         (0.025840100000000005, 0.0696384),
#         (0.022988900000000003, 0.062505),
#     ],
#     [
#         (0.6253753000000001, 1.28214),
#         (0.1954469, 0.5621571000000001),
#         (0.0539253, 0.1456434),
#         (0.040008100000000005, 0.1039365),
#         (0.034810600000000004, 0.0896688),
#         (0.0303666, 0.0806139),
#     ],
#     [
#         (0.7246415000000002, 1.4577453),
#         (0.2269707, 0.6543504),
#         (0.06532790000000001, 0.179667),
#         (0.0493988, 0.135216),
#         (0.04369750000000001, 0.11875320000000002),
#         (0.03799620000000001, 0.1066806),
#     ],
#     [
#         (1.0412182, 1.28214),
#         (0.3087975, 0.559962),
#         (0.07538850000000001, 0.1374111),
#         (0.0534226, 0.0968031),
#         (0.044368500000000005, 0.08308349999999999),
#         (0.038834400000000005, 0.0745776),
#     ]
# ]

# builds heatmaps
q.heatmaps(plot=False,
            save_path='out/analysis',
            plot_mode='fiber0',
        #    rows_override=6,
           colorbar_aspect=5,
           colormap_str='viridis',
           tick_count=4,
           reverse_colormap=True,
        #    title_toggle=False,
        #    track_colormap_bounds=True,
        #    track_colormap_bounds_offset_ratio=0.0,
        #    colomap_bounds_override=colormap_bounds_override,
        #    subplot_title_toggle=False,
            colorbar_text_size_override=30
        #    tick_bounds=True
           )

#
#                 # TODO: Finish building heatmap of polyfasc nerve (1 fiber/fasc)
#                 # also, look into adding documentation to Simulation (might be useful for above task too)

#plt.close('all')
