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

sys.path.append(os.path.sep.join([os.getcwd(), '']))
from src.core.query import Query  # noqa E402

sns.set_style("whitegrid")

fiber_indices = [0]

q = Query(
    {
        'partial_matches': False,
        'include_downstream': True,
        'indices': {'sample': [0], 'model': [0], 'sim': [0]},
    }
).run()

data = q.sfap_data(fiber_indices=fiber_indices, all_fibers=True)
print(data)

# for fiber in
fig, ax = plt.subplots()
sns.lineplot(data=data, x='SFAP_times', y='SFAP0', hue='fiberset_index', palette='deep', ax=ax)
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
plt.xlim(left=0, right=10.0)
plt.title('Single Fiber Action Potentials')
plt.xlabel('Time (ms)')
plt.ylabel(r'signal (${\mu}V$)')
plt.show()
