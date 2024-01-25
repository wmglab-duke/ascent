#!/usr/bin/env python3.7

"""Plot the compound nerve action potential (CNAP).

The recorded SFAPs are produced for every fiber when a model contains a
recording cuff, identified within the model.json configuration file. The user
may pass in specific fiber indices or choose to compound across all fibers.

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

fiber_indices = list(range(13))
print(fiber_indices)

q = Query(
    {
        'partial_matches': False,
        'include_downstream': True,
        'indices': {'sample': [0], 'model': [0], 'sim': [0]},
    }
).run()
data = q.sfap_data(fiber_indices, all_fibers=True)

# CNAP = Summation of all fibers
cnap = data.groupby(['SFAP_times'])['SFAP0'].sum().reset_index()

# Generate plot
sns.lineplot(data=cnap, x='SFAP_times', y='SFAP0')
plt.title('Compound Neuron Action Potential')
plt.xlabel('Time (ms)')
plt.ylabel(r'signal (${\mu}V$)')
plt.xlim(left=0, right=4.5)
plt.show()
