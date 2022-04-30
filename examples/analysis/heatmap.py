#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

# RUN THIS FROM REPOSITORY ROOT

# ASSUMPTIONS: (old, moved to Query.heatmaps)
#   1) 1:1 inner:outer for all fascicles
#   2) Single slide for each sample (0_0)
#   3) Single fiber per inner
# TODO: Change above assumptions in later iteration? (highest priority is probably assumption 3)

import os
import sys

sys.path.append(os.path.sep.join([os.getcwd(), '']))
from src.core.query import Query

# # set default fig size
# plt.rcParams['figure.figsize'] = [16.8/3, 10.14*2 * 0.9]

# initialize and run Querys
q = Query({
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'sample': [18],
        'model': [451],
        'sim': [1,18]
    }
}).run()

# NOTE: these values were copied from the output of heatmaps(), setting the track_colormap_bounds flag True
colormap_bounds_override = None

# builds heatmaps
q.heatmaps(plot=False,
            save_path='out/analysis',
            plot_mode='fibers',
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
# plt.tight_layout()
