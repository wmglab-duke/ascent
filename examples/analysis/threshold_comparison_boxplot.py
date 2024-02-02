"""Compare thresholds across models using a boxplot.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent.

For more controls over how the plotting occurs, see the seaborn documentation on barplot:
https://seaborn.pydata.org/generated/seaborn.boxplot.html
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
g = sns.boxplot(data=data, x='model', y='threshold')
plt.title('Threshold boxplot comparison')

save_directory = os.path.join('output', 'analysis')
os.makedirs(save_directory, exist_ok=True)
plt.savefig(os.path.join('threshold_comparison_boxplot.png', save_directory), dpi=400, bbox_inches='tight')
