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

# initialize and run Querys
q = Query({
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'sample': [1001],
        'model': [0, 1, 2, 3],
        'sim': [1005, 1006]
    }
}).run()
#


q.heatmaps(plot=True,
           save_path='D:\\Documents\\ascent_logs\\heatmaps_figures',
           colorbar_aspect=6,
           title_toggle=False,
           track_colormap_bounds=True,
           track_colormap_bounds_offset_ratio=0.0,
           subplot_title_toggle=False,
           colorbar_text_size_override=100,
           tick_bounds=True,
           show_orientation_point=True,
           plot_mode='fibers',
           colormap_str='viridis'
           )

#                 # TODO: Finish building heatmap of polyfasc nerve (1 fiber/fasc)
#                 # also, look into adding documentation to Simulation (might be useful for above task too)

plt.close('all')
