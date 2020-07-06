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

#initialize and run Querys
q = Query({
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'sample': [80],
        'model': [0],
        'sim': [12]
    }
}).run()
#


# 10
# colormap_bounds_override = [
#     (0.373516, 3),
#     (0.090002, 0.735098),
#     (0.053748, 0.301973),
#     (0.04843, 0.246865),
#     (0.287471, 3),
#     (0.064382, 0.667422),
#     (0.036466, 0.264268),
#     (0.032599, 0.214961),
#     (0.285537, 3),
#     (0.067041, 0.899453),
#     (0.040092, 0.361914),
#     (0.035862, 0.295205),
#     (0.259434, 3),
#     (0.06269, 0.87625),
#     (0.038279, 0.353213),
#     (0.034895, 0.288438),
#     (0.252666, 3),
#     (0.057615, 0.570742),
#     (0.033324, 0.235264),
#     (0.029819, 0.192725),
#     (0.33291, 3),
#     (0.084202, 0.648086),
#     (0.051331, 0.275869),
#     (0.045771, 0.228496),
# ]

# 10 clipped
# colormap_bounds_override = [
#     (0.373516, 3),
#     (0.090002, 0.899453),
#     (0.053748, 0.361914),
#     (0.04843, 0.295205),
#     (0.373516, 3),
#     (0.090002, 0.899453),
#     (0.053748, 0.361914),
#     (0.04843, 0.295205),
#     (0.373516, 3),
#     (0.090002, 0.899453),
#     (0.053748, 0.361914),
#     (0.04843, 0.295205),
#     (0.373516, 3),
#     (0.090002, 0.899453),
#     (0.053748, 0.361914),
#     (0.04843, 0.295205),
#     (0.373516, 3),
#     (0.090002, 0.899453),
#     (0.053748, 0.361914),
#     (0.04843, 0.295205),
#     (0.373516, 3),
#     (0.090002, 0.899453),
#     (0.053748, 0.361914),
#     (0.04843, 0.295205),
# ]

# 12
# colormap_bounds_override = [
#     (0.406387, 3),
#     (0.082751, 3),
#     (0.050605, 3),
#     (0.046497, 3),
#     (0.303906, 3),
#     (0.075984, 3),
#     (0.048672, 3),
#     (0.045046, 3),
#     (0.270068, 3),
#     (0.060273, 1.412979),
#     (0.036224, 0.592012),
#     (0.033203, 0.495332),
#     (0.246865, 3),
#     (0.058098, 1.258758),
#     (0.03562, 0.566875),
#     (0.032841, 0.47793)
# ]

# colormap_bounds_override = [
#     (0.329043, 3),
#     (0.079609, 3),
#     (0.049639, 3),
#     (0.044926, 3),
#     (0.382217, 3),
#     (0.087102, 3),
#     (0.051572, 3),
#     (0.046255, 3),
#     (0.241064, 3),
#     (0.057373, 1.057422),
#     (0.035741, 0.48373),
#     (0.032841, 0.410254),
#     (0.322275, 3),
#     (0.061482, 1.181875),
#     (0.036587, 0.506934),
#     (0.033566, 0.427656)
# ]

q.heatmaps(plot=True,
           save_path='D:\Documents\LivaNovaContact\Pig191205-0\heatmaps',
           rows_override=4, #6
           colorbar_aspect=5,
           title_toggle=False,
           track_colormap_bounds=True,
           track_colormap_bounds_offset_ratio=0.0,
           # colomap_bounds_override=colormap_bounds_override,
           subplot_title_toggle=False,
           colorbar_text_size_override=40,
           tick_bounds=True,
           show_orientation_point=True,
           colormap_str='BuPu'
           )

#                 # TODO: Finish building heatmap of polyfasc nerve (1 fiber/fasc)
#                 # also, look into adding documentation to Simulation (might be useful for above task too)

plt.close('all')
