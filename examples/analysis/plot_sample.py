#!/usr/bin/env python3.7

import os
import sys

root = os.path.abspath(os.path.join(*'../../'.split('/')))
sys.path.append(root)

from src.core import Sample
from src.core.query import Query
from src.utils import Object
import matplotlib.pyplot as plt

cwd = os.getcwd()
os.chdir(root)

criteria = {
    'partial_matches': True,
    'include_downstream': False,
    'indices': {
        'sample': [88],
        'model': None,
        'sim': None
    }
}


q = Query(criteria)
q.run()

results = q.summary()

sample_index = results['samples'][0]['index']

fig, ax = plt.subplots(1, 1)
item: Sample = q.get_object(Object.SAMPLE, [results['samples'][0]['index']])
slide = item.slides[0]
slide.plot(fix_aspect_ratio=True, final=False, ax=ax, inner_index_labels=True)
plt.xlabel('\u03bcm')
plt.ylabel('\u03bcm')
plt.show()

fname = str(sample_index)
fmt = 'svg'

dest = os.path.join('data', 'tmp', 'samples')
if not os.path.exists(dest):
    os.mkdir(dest)

fig.savefig(os.path.join(dest, '{}.{}'.format(fname, fmt)), format=fmt, dpi=1200)

os.chdir(cwd)
