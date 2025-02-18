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
os.chdir('../..')
from src.core.query import Query  # noqa E402

sns.set_style("white")

fiber_indices = [0]

q = Query(
    {
        'partial_matches': False,
        'include_downstream': True,
        'indices': {'sample': [1], 'model': [0], 'sim': [113]},
    }
).run()

data = q.common_data_extraction(data_types=['sfap'])

# explode the data and plot all at once using seaborn.
splode = data.explode(['SFAP_times', 'SFAP'], ignore_index=True)

# plot the data
fig, ax = plt.subplots()
sns.lineplot(data=splode, x='SFAP_times', y='SFAP', hue='fiberset_index', palette='viridis', ax=ax)
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
plt.xlim(left=0, right=30)
plt.title('Single Fiber Action Potentials')
plt.xlabel('Time (ms)')
plt.ylabel(r'signal (${\mu}V$)')
plt.axhline(0, c='k', ls='--')
plt.show()
