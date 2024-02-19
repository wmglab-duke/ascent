"""Generate dose-response curves (% fibers activated as a function of stimulation amplitude).

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent.

For more controls over how the plotting occurs, see the seaborn documentation on ecdfplot:
https://seaborn.pydata.org/generated/seaborn.ecdfplot.html#seaborn.ecdfplot
RUN THIS FROM REPOSITORY ROOT
"""

import os
import sys

import matplotlib.pyplot as plt
import seaborn as sb

sys.path.append(os.path.sep.join([os.getcwd(), '']))

from src.core.query import Query

sb.set_theme()

q = Query(
    {
        'partial_matches': False,
        'include_downstream': True,
        'indices': {'sample': [0], 'model': [0], 'sim': [0]},
    }
).run()

data = q.threshold_data()
g = sb.ecdfplot(data=data, x='threshold')
plt.ylabel('Percent of fibers activated')
plt.title('Dose-response curve')
plt.savefig('dose_response_curves.png', dpi=400, bbox_inches='tight')
