#!/usr/bin/env python3.7

import os
import sys

root = os.path.abspath(os.path.join(*'../../'.split('/')))
sys.path.append(root)

from src.core import Sample
from src.core.query import Query
from src.utils import Object
import matplotlib.pyplot as plt
import numpy as np


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
slide = item.slides[0]
slide.plot(fix_aspect_ratio=True, inner_index_labels=True, final=False)

# four electrode orientations
if slide.orientation_point_index is not None:
    d_thetas = np.arange(0, 2*np.pi, np.pi / 2)
    colors = [(20, 124, 180), (244, 124, 36), (44, 164, 76), (212, 44, 43)]

    for (d_theta, color) in zip(d_thetas, colors):

        r = slide.nerve.mean_radius() * 1.15  # scale up so orientation point is outside nerve
        theta = np.arctan2(*tuple(np.flip(slide.nerve.points[slide.orientation_point_index][:2]))) + d_theta
        orientation_point = r * np.cos(theta), r * np.sin(theta)
        plt.plot(*orientation_point, '.', markersize=20, color=tuple(c / 255.0 for c in color))

plt.gca().axis('off')
plt.show()

os.chdir(cwd)
