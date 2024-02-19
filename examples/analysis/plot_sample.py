"""Plot a sample.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent.

RUN THIS FROM REPOSITORY ROOT
"""

import os
import sys

sys.path.append(os.path.sep.join([os.getcwd(), '']))

import matplotlib.pyplot as plt

from src.core import Sample
from src.core.query import Query
from src.utils import Object

criteria = {
    'partial_matches': True,
    'include_downstream': False,
    'indices': {'sample': [0], 'model': None, 'sim': None},
}


q = Query(criteria)
q.run()

results = q.summary()

sample_index = results['samples'][0]['index']

fig, ax = plt.subplots(1, 1)
item: Sample = q.get_object(Object.SAMPLE, [results['samples'][0]['index']])
slide = item.slides[0]
slide.plot(
    fix_aspect_ratio=True,
    final=False,
    ax=ax,
    inner_index_labels=True,
    scalebar=True,
    scalebar_length=100,
    scalebar_units='μm',
)
plt.xlabel('\u03bcm')
plt.ylabel('\u03bcm')
plt.show()

fname = str(sample_index)
fmt = 'svg'

dest = os.path.join('data', 'tmp', 'samples')
if not os.path.exists(dest):
    os.mkdir(dest)

fig.savefig(os.path.join(dest, f'{fname}.{fmt}'), format=fmt, dpi=1200)
