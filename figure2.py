import os
import pickle

import numpy as np

from src.core import Deformable
from src.utils import ReshapeNerveMode

sample_num = 24


def load(path: str):
    return pickle.load(open(path, 'rb'))


sample_file = os.path.join(
    'plotting_samples',
    'sample{}.obj'.format(sample_num)
)

# instantiate sample
sample = load(sample_file)

left = -3000
right = 3000
up = 1500
down = -1500

morph_count = 36
# title = 'morph count: {}'.format(morph_count)
dist = 10
deform_animate = True

# figure1 = plt.figure(1)
for slide in sample.slides:
    bounds = slide.nerve.polygon().bounds
    width = int(1.5 * (bounds[2] - bounds[0]))
    height = int(1.5 * (bounds[3] - bounds[1]))

    slide.move_center(np.array([width/2, height/2]))
    deformable = Deformable.from_slide(slide,
                                       ReshapeNerveMode.CIRCLE,
                                       minimum_distance=dist)

    movements, rotations = deformable.deform(morph_count=morph_count,
                                             render=deform_animate,
                                             minimum_distance=dist)

# plt.axes().set_aspect('equal')
# plt.xlim(left, right)
# plt.ylim(down, up)
# plt.show()
# figure1.savefig('C:\\Users\\edm23\\Desktop\\pipeline_figures\\image_segmentation\\nerve.svg', format='svg', dpi=1200)
