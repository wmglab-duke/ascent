#!/usr/bin/env python3.7

import os

from src.core import Sample
from src.core import Simulation
from src.core.query import Query
from src.utils import Object

ind = 1
criteria: str = os.path.join('config', 'user', 'query_criteria', '{}.json'.format(ind))
q = Query(criteria)
q.run()
results = q.summary()

sam: Sample = q.get_object(Object.SAMPLE, [results['samples'][0]['index']])
sam.slides[0].plot()

sim: Simulation = q.get_object(Object.SIMULATION, [results['samples'][0]['models'][0]['sims'][0]])
print('here')

