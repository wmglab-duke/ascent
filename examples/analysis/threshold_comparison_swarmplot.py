#!/usr/bin/env python3.7

"""Compare thresholds across models using a boxplot.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent.

For more controls over how the plotting occurs, see the seaborn documentation on barplot:
https://seaborn.pydata.org/generated/seaborn.swarmplot.html
RUN THIS FROM REPOSITORY ROOT
"""

import os

import matplotlib.pyplot as plt
import seaborn as sns

from src.core.query import Query

sns.set_theme()

q = Query(
    {
        'partial_matches': False,
        'include_downstream': True,
        'indices': {'sample': [0], 'model': [0, 1], 'sim': [0]},
    }
).run()

data = q.threshold_data()
g = sns.swarmplot(data=data, x='model', y='threshold')
plt.title('Threshold swarmplot comparison')

save_directory = os.path.join('output', 'analysis')
os.makedirs(save_directory, exist_ok=True)
plt.savefig(os.path.join(save_directory, 'threshold_comparison_swarmplot.png'), dpi=400, bbox_inches='tight')
