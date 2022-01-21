#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE.txt and README.txt files for licensing instructions.
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

microamps = True

sys.path.append(os.path.sep.join([os.getcwd(), '']))
os.chdir('D:/ASCENT/m18')
import matplotlib.pyplot as plt
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
        'sim': [20]
    }
}).run()

# NOTE: these values were copied from the output of heatmaps(), setting the track_colormap_bounds flag True
colormap_bounds_override = None

# builds heatmaps
useless, also_useless, bounds = q.heatmaps(plot=False,
            save_path='out/analysis',
            plot_mode='fibers',
        #    rows_override=6,
           colorbar_aspect=5,
           colormap_str='viridis',
           tick_count=4,
           reverse_colormap=True,
           alltitle = False,
           colorbar_mode='subplot',
        #    title_toggle=False,
            track_colormap_bounds=True,
        #    track_colormap_bounds_offset_ratio=0.0,
        #    colomap_bounds_override=colormap_bounds_override,
        #    subplot_title_toggle=False,
            colorbar_text_size_override=30,
            # min_max_ticks=True,
            microamps = microamps
        #    tick_bounds=True
           )


superbound = [[min([x[0] for x in bounds]),max([x[1] for x in bounds])] for i in range(len(bounds))]


q.heatmaps(plot=False,
            # save_path='out/analysis',
            plot_mode='fibers',
        #    rows_override=6,
           colorbar_aspect=5,
           colormap_str='viridis',
           tick_count=4,
           reverse_colormap=True,
            track_colormap_bounds=False,
        #    track_colormap_bounds_offset_ratio=0.0,
            colomap_bounds_override=superbound,
        #    subplot_title_toggle=False,
            colorbar_text_size_override=30,
            add_colorbar = False,
            microamps = microamps
        #    tick_bounds=True
       )


# plt.subplots_adjust(wspace = 0)
fig = plt.gcf()
fig.subplots_adjust(right=0.8)
cbar_ax = fig.add_axes([0.8, 0.15, 0.05, 0.7])

cmap = plt.get_cmap('viridis')
cmap = cmap.reversed()
mp = plt.cm.ScalarMappable(cmap=cmap)
mp.set_clim(superbound[0][0],superbound[0][1])

cb= fig.colorbar(
mappable=mp,
orientation='vertical',
aspect=20,
format='%0.2f',
cax = cbar_ax,
)
cb.ax.tick_params(labelsize = 50)
cb.ax.tick_params(size = 15)
cb.ax.tick_params(width = 5)
if not microamps:
    cbar_ax.set_title(r'mA',fontsize = 50)
else:
    cbar_ax.set_title(u'\u03bcA',fontsize = 50)
colorbar_text_size_override = 100
# colorbar font size
# if colorbar_text_size_override is not None:
#     cb.ax.tick_params(labelsize=colorbar_text_size_override if (
#             colorbar_text_size_override is not None) else 25)
# cb.update_ticks()
# fig.subplots_adjust(left=.15)
# fig.subplots_adjust(top=.95)

fig.savefig('out/analysis/3dhm.png',dpi=500)
