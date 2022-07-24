#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE.txt and README.txt files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

# RUN THIS FROM REPOSITORY ROOT
import os
import sys

import matplotlib.pyplot as plt

from src.core.query import Query

sys.path.append(os.path.sep.join([os.getcwd(), '']))

params = {
    'outpath': 'out/analysis',
    'sample': 18,
    'model': 451,
    'sim': 18,
    'microamps': False,
    'title': 'Activation Thresholds: Cadaver57-3',
    'title_shared': 'Activation Thresholds: Cadaver57-3',
}


def run_heatmaps(params):

    # initialize and run Querys
    q = Query(
        {
            'partial_matches': True,
            'include_downstream': True,
            'indices': {
                'sample': [params['sample']],
                'model': [params['model']],
                'sim': [params['sim']],
            },
        }
    ).run()

    # NOTE: these values were copied from the output of heatmaps(), setting the track_colormap_bounds flag True

    # builds heatmaps
    useless, also_useless, bounds = q.heatmaps(
        plot=False,
        save_path=params['outpath'],
        plot_mode='fibers',
        colorbar_aspect=5,
        colormap_str='viridis',
        tick_count=4,
        reverse_colormap=True,
        alltitle=False,
        colorbar_mode='subplot',
        dotsize=5,
        track_colormap_bounds=True,
        colorbar_text_size_override=30,
        microamps=params['microamps'],
        min_max_ticks=True,
        suptitle_override=params['title'],
    )

    superbound = [[min([x[0] for x in bounds]), max([x[1] for x in bounds])] for i in range(len(bounds))]

    q.heatmaps(
        plot=False,
        plot_mode='fibers',
        colorbar_aspect=5,
        colormap_str='viridis',
        tick_count=4,
        dotsize=5,
        alltitle=False,
        reverse_colormap=True,
        track_colormap_bounds=False,
        colomap_bounds_override=superbound,
        colorbar_text_size_override=30,
        add_colorbar=False,
        microamps=params['microamps'],
        suptitle_override=params['title_shared'],
    )

    fig = plt.gcf()
    fig.subplots_adjust(right=0.8, wspace=0.1)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.02, 0.7])

    cmap = plt.get_cmap('viridis')
    cmap = cmap.reversed()
    mp = plt.cm.ScalarMappable(cmap=cmap)
    mp.set_clim(superbound[0][0], superbound[0][1])

    cb = fig.colorbar(
        mappable=mp,
        orientation='vertical',
        aspect=20,
        format='%0.2f',
        cax=cbar_ax,
    )
    cb.ax.tick_params(labelsize=50)
    cb.ax.tick_params(size=15)
    cb.ax.tick_params(width=5)
    if not params['microamps']:
        cbar_ax.set_title(r'mA', fontsize=50)
    else:
        cbar_ax.set_title(u'\u03bcA', fontsize=50)
    dest = '{}{}{}_{}_{}_shared_cbar.png'.format(
        params['outpath'], os.sep, params['sample'], params['model'], params['sim']
    )
    fig.savefig(dest, dpi=500)


run_heatmaps(params)
