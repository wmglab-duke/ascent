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
plt.rcParams['figure.figsize'] = [16.8 / 3, 10.14 * 2 * 0.9]

# NOTE: these values were copied from the output of heatmaps(), setting the track_colormap_bounds flag True

# RAW
# colormap_bounds_override = [
#     [
#         (0.502671, 3.951367),
#         (0.100242, 0.883149),
#         (0.056798, 0.335602),
#         (0.051005, 0.270969),
#         (0.391698, 4.907441),
#         (0.072498, 0.807542),
#         (0.03881, 0.296578),
#         (0.03439, 0.236824),
#         (0.385601, 7.736641),
#         (0.074328, 1.083145),
#         (0.042316, 0.405112),
#         (0.037591, 0.322187),
#         (0.347797, 3.824541),
#         (0.069145, 1.058755),
#         (0.040335, 0.394137),
#         (0.036524, 0.31609),
#         (0.341699, 5.024512),
#         (0.064877, 0.688032),
#         (0.035304, 0.263652),
#         (0.031341, 0.212434),
#         (0.445355, 5.473281),
#         (0.09323, 0.770957),
#         (0.054054, 0.307554),
#         (0.047804, 0.249019),
#     ]
# ]

# USED

#initialize and run Querys
q = Query({
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'sample': [80],
        'model': [0],
        'sim': [10]
    }
}).run()
#
# colormap_bounds_override = [
#     [
#         (0.341699, 7.736641),
#         (0.064877, 1.083145),
#         (0.035304, 0.405112),
#         (0.031341, 0.322187),
#         (0.341699, 7.736641),
#         (0.064877, 1.083145),
#         (0.035304, 0.405112),
#         (0.031341, 0.322187),
#         (0.341699, 7.736641),
#         (0.064877, 1.083145),
#         (0.035304, 0.405112),
#         (0.031341, 0.322187),
#         (0.341699, 7.736641),
#         (0.064877, 1.083145),
#         (0.035304, 0.405112),
#         (0.031341, 0.322187),
#         (0.341699, 7.736641),
#         (0.064877, 1.083145),
#         (0.035304, 0.405112),
#         (0.031341, 0.322187),
#         (0.341699, 7.736641),
#         (0.064877, 1.083145),
#         (0.035304, 0.405112),
#         (0.031341, 0.322187),
#     ]
# ]
#
# #builds heatmaps
q.heatmaps(plot=True,
           save_path='D:\Documents\LivaNovaContact\Pig191205-0\heatmaps',
           rows_override=6,
           colorbar_aspect=5,
           title_toggle=False,
           track_colormap_bounds=True,
           track_colormap_bounds_offset_ratio=0.0,
           #colomap_bounds_override=colormap_bounds_override,
           subplot_title_toggle=True,
           colorbar_text_size_override=20,
           tick_bounds=True,
           show_orientation=True,
           colormap_str='BuPu'
           )

# # initialize and run Querys
# q = Query({
#     'partial_matches': True,
#     'include_downstream': True,
#     'indices': {
#         'sample': [80],
#         'model': [0],
#         'sim': [12]
#     }
# }).run()

# colormap_bounds_override = [
#     [
#         (0.303895, 57.576136),
#         (0.076157, 12.005547),
#         (0.048719, 6.800078),
#         (0.04506, 5.902539),
#         (0.406332, 43.078497),
#         (0.082864, 10.785352),
#         (0.050395, 6.526914),
#         (0.046584, 5.707422),
#         (0.247799, 7.775664),
#         (0.058017, 1.25875),
#         (0.035609, 0.566084),
#         (0.032865, 0.477062),
#         (0.270969, 8.126875),
#         (0.060304, 1.409966),
#         (0.036219, 0.590474),
#         (0.033323, 0.495354),
#     ]
# ]

# colormap_bounds_override = [
#     [
#             (0.303895, 57.576136),
#             (0.076157, 12.005547),
#             (0.048719, 6.800078),
#             (0.04506, 5.902539),
#             (0.303895, 57.576136),
#             (0.076157, 12.005547),
#             (0.048719, 6.800078),
#             (0.04506, 5.902539),
#
#             (0.247799, 8.126875),
#             (0.058017, 1.409966),
#             (0.035609, 0.590474),
#             (0.032865, 0.495354),
#             (0.247799, 8.126875),
#             (0.058017, 1.409966),
#             (0.035609, 0.590474),
#             (0.032865, 0.495354),
#         ]
# ]

# colormap_bounds_override = [
#     [
#         (0.303895, 20),
#         (0.076157, 5),
#         (0.048719, 1),
#         (0.04506, 0.5),
#         (0.303895, 20),
#         (0.076157, 5),
#         (0.048719, 1),
#         (0.04506, 0.5),
#         (0.247799, 8),
#         (0.058017, 1),
#         (0.035609, 0.5),
#         (0.032865, 0.5),
#         (0.247799, 8),
#         (0.058017, 1),
#         (0.035609, 0.5),
#         (0.032865, 0.5)
#     ]
# ]
#
# q.heatmaps(plot=True,
#            save_path='D:\Documents\LivaNovaContact\Pig191205-0\heatmaps',
#            rows_override=4,
#            colorbar_aspect=5,
#            title_toggle=False,
#            track_colormap_bounds=True,
#            track_colormap_bounds_offset_ratio=0,
#            #colomap_bounds_override=colormap_bounds_override,
#            subplot_title_toggle=True,
#            colorbar_text_size_override=20,
#            tick_bounds=True,
#            show_orientation=True,
#            colormap_str='BuPu'
#            )

#
#                 # TODO: Finish building heatmap of polyfasc nerve (1 fiber/fasc)
#                 # also, look into adding documentation to Simulation (might be useful for above task too)

plt.close('all')
