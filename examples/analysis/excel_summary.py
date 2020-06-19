#!/usr/bin/env python3.7

# RUN THIS FROM REPOSITORY ROOT

import os
import sys

sys.path.append(os.path.sep.join([os.getcwd(), '']))

from src.core.query import Query


# initialize and run Querys
q = Query({
    'partial_matches': True,
    'include_downstream': True,
    'indices': {
        'sample': [3, 4, 5, 6],
        'model': [0, 1, 2, 3],
        'sim': [0, 1]
    }
}).run()

q.excel_output(
    '/Users/jakecariello/Desktop/test.xlsx',
    sample_keys=[
        ['sample'],
        ['sex']
    ],
    model_keys=[
        ['cuff', 'rotate', 'add_ang']
    ]
)