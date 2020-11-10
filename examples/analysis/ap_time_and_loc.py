import os
import sys

sys.path.append(os.path.sep.join([os.getcwd(), '']))

import numpy as np

import matplotlib.pyplot as plt
from src.core.query import Query

# set default fig size
# plt.rcParams['figure.figsize'] = list(np.array([16.8, 10.14]) / 2)

q = Query({
    'partial_matches': False,
    'include_downstream': True,
    'indices': {
        'sample': [0],
        'model': [0, 1, 2],
        'sim': [1]
    }
}).run()

q.ap_time_and_location(delta_V=80, absolute_voltage=False)
