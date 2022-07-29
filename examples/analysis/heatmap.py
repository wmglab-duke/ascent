#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent

Generate a heatmap of activation thresholds.
"""

# RUN THIS FROM REPOSITORY ROOT

import os
import sys

from src.core.query import Query

sys.path.append(os.path.sep.join([os.getcwd(), '']))


# initialize and run Querys
q = Query(
    {
        'partial_matches': True,
        'include_downstream': True,
        'indices': {'sample': [18], 'model': [451], 'sim': [1, 18]},
    }
).run()

# builds heatmaps
q.heatmaps(
    plot=False,
    save_path='out/analysis',
    plot_mode='fibers',
    colorbar_aspect=5,
    colormap_str='viridis',
    tick_count=4,
    reverse_colormap=True,
    colorbar_text_size_override=30,
)
