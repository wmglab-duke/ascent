#!/usr/bin/env python3.7

"""Generate a heatmap of activation thresholds.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent.

Note: if more than one heatmap is desired, you must use a Seaborn FacetGrid.
RUN THIS FROM REPOSITORY ROOT
"""

import matplotlib.pyplot as plt

from src.core.plotter import heatmaps
from src.core.query import Query

# Initialize and run Querys
q = Query(
    {
        'partial_matches': True,
        'include_downstream': True,
        'indices': {'sample': [0], 'model': [0], 'sim': [0]},
    }
).run()

# Build heatmap
heatmaps(data=q.threshold_data(), cuff_orientation=True)
plt.title('Activation threshold heatmap')
