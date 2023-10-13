#!/usr/bin/env python3.7

"""Plot single or multiple overlaid Single Fiber Action Potentials (SFAP).

The recorded SFAPs are produced for every fiber when a model contains a
recording cuff, identified within the model.json configuration file.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent.
"""

import os
import sys

import matplotlib.pyplot as plt
import seaborn as sns

from src.core.query import Query

sys.path.append(os.path.sep.join([os.getcwd(), '']))
sns.set_style("whitegrid")

fiber_indices = [0, 58, 75, 120, 191, 192]

q = Query(
    {
        'partial_matches': False,
        'include_downstream': True,
        'indices': {'sample': [20230323], 'model': [0], 'sim': [2023032309]},
    }
).run()

data = q.sfap_data(fiber_indices)
print(data)

# for fiber in
sns.lineplot(data=data, x='SFAP_times', y='SFAP0', hue='fiberset_index', palette='deep')
plt.xlim(left=0, right=4.5)
plt.show()
