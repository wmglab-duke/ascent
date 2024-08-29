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
os.chdir('../..')
from src.core.query import Query  # noqa E402

sns.set_style("white")

fiber_indices = list(range(13))
print(fiber_indices)

q = Query(
    {
        'partial_matches': False,
        'include_downstream': True,
        'indices': {'sample': [1], 'model': [0], 'sim': [113]},
    }
).run()
data = q.common_data_extraction(data_types=['sfap'])

splode = data.explode(['SFAP_times', 'SFAP'], ignore_index=True)

# CNAP = Summation of all fibers
cnap = splode.groupby(['SFAP_times'])['SFAP'].sum().reset_index()

# Generate plot
plt.axhline(0, color='grey', ls='-', lw=0.75)
sns.lineplot(data=cnap, x='SFAP_times', y='SFAP', color='k')
plt.title('Compound Neuron Action Potential')
plt.xlabel('Time (ms)')
plt.ylabel(r'signal (${\mu}V$)')
plt.show()
