#!/usr/bin/env python3.7

import os
import sys

root = os.path.abspath(os.path.join(*'../../'.split('/')))
sys.path.append(root)

from src.core import Sample
from src.core.query import Query
from src.utils import Object



cwd = os.getcwd()


os.chdir(root)

criteria = {
    'partial_matches': True,
    'include_downstream': False,
    'indices': {
        'sample': [3],
        'model': None,
        'sim': None
    }
}


q = Query(criteria)
q.run()

results = q.summary()

item: Sample = q.get_object(Object.SAMPLE, [results['samples'][0]['index']])
item.slides[0].plot(fix_aspect_ratio=True, inner_index_labels=True)

os.chdir(cwd)
