#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE.txt and README.txt files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

# Returns nsim thresholds from the selected sample/model/sim combos as a dataframe
# Use arg meanify=True to instead get the mean threshold for each nsim with stats

# RUN THIS FROM REPOSITORY ROOT

#%% imports
import os
import sys

sys.path.append(os.path.sep.join([os.getcwd(), '']))

from src.core.query import Query

#%% metadata
samples = [670,672]

models = [0]

sims = [33]

dats = []

#%% run query search
q = Query({
    'partial_matches': False,
    'include_downstream': True,
    'indices': {
        'sample': samples,
        'model': models,
        'sim': sims
    }
}).run()

#%% obtain thresholds
data = q.threshdat(meanify=False)
