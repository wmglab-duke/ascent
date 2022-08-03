#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent

Generate a heatmap of activation thresholds.
"""

# RUN THIS FROM REPOSITORY ROOT
from src.core.plotter import heatmaps
from src.core.query import Query

# initialize and run Querys
q = Query(
    {
        'partial_matches': True,
        'include_downstream': True,
        'indices': {'sample': [0], 'model': [0], 'sim': [0]},
    }
).run()

# builds heatmaps
fig, axes, colormap_bounds = heatmaps(
    q,
    plot=False,
    plot_mode='fibers',
    colorbar_aspect=5,
    colormap_str='viridis',
    tick_count=4,
    reverse_colormap=True,
    colorbar_text_size_override=30,
)
fig.savefig('heatmap.png', dpi=400, bbox_inches='tight')
