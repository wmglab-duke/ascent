#!/usr/bin/env python3.7

# RUN THIS FROM REPOSITORY ROOT

import os
import sys

sys.path.append(os.path.sep.join([os.getcwd(), '']))

import numpy as np

import matplotlib.pyplot as plt
from src.core.query import Query

# set default fig size
plt.rcParams['figure.figsize'] = list(np.array([16.8, 10.14]) / 2)

# initialize and run Querys
q = Query({
    'partial_matches': True,
    'include_downstream': False,
    'indices': {
        'sample': [7],
        'model': [0],
        'sim': [1]
    }
}).run()

# q.barcharts_compare_samples_2(model_labels=['0'],
#                               sample_labels=['0.5 cm', '2 cm', '5 cm', '7.8 cm'],
#                               title='i50 at 4 longitudinal positions (merged)',
#                               ylabel='i50 (mA)',
#                               calculation='i50',
#                               merge_bars=True,
#                               width=0.9,
#                               logscale=True)

q.barcharts_compare_samples(
    # model_labels=['0 for LivaNova and all mapping electrode positions'],
                            #   sample_labels=['LivaNova (0.8cm)', 'Mapping (0.5 cm)', 'Mapping (2 cm)', 'Mapping (5 cm)', 'Mapping (7.8 cm)'],
                              # title='i50 at 4 longitudinal positions (merged)',
                              # ylabel='i50 (mA)',
                              # calculation='i50',
                              merge_bars=True,
                              # width=0.9,
                            #   logscale=True,
                              label_bar_heights=True,
                              plot=True,
                              model_labels=['MRG SL, LivaNova Cuff']
                              )

plt.tight_layout()
plt.show()

# q.barcharts_compare_samples_2(sample_labels=[''],
#                               # title='i50 at 4 longitudinal positions (merged)',
#                               # ylabel='i50 (mA)',
#                               # calculation='i50',
#                               # merge_bars=True,
#                               # width=0.9,
#                               logscale=False,
#                               label_bar_heights=True
#                               )