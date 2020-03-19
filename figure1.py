import os

import pickle
from matplotlib import pyplot as plt

from src.core import Sample

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

figure1 = plt.figure(1)
for slide in sample.slides:
    slide.nerve.plot('k-')
plt.axes().set_aspect('equal')
plt.xlim(left, right)
plt.ylim(down, up)
plt.show()
figure1.savefig('C:\\Users\\edm23\\Desktop\\pipeline_figures\\image_segmentation\\nerve.svg', format='svg', dpi=1200)

figure2 = plt.figure(2)
for slide in sample.slides:
    for fascicle in slide.fascicles:
        fascicle.plot('k-')
plt.axes().set_aspect('equal')
plt.xlim(left, right)
plt.ylim(down, up)
plt.show()
figure2.savefig('C:\\Users\\edm23\\Desktop\\pipeline_figures\\image_segmentation\\combined.svg', format='svg', dpi=1200)

figure3 = plt.figure(3)
for slide in sample.slides:
    for fascicle in slide.fascicles:
        for inner in fascicle.inners:
            inner.plot('k-')
plt.axes().set_aspect('equal')
plt.xlim(left, right)
plt.ylim(down, up)
plt.show()
figure3.savefig('C:\\Users\\edm23\\Desktop\\pipeline_figures\\image_segmentation\\inners.svg', format='svg', dpi=1200)

figure4 = plt.figure(4)
for slide in sample.slides:
    for fascicle in slide.fascicles:
        fascicle.outer.plot('k-')
plt.axes().set_aspect('equal')
plt.xlim(left, right)
plt.ylim(down, up)
plt.show()
figure4.savefig('C:\\Users\\edm23\\Desktop\\pipeline_figures\\image_segmentation\\outers.svg', format='svg', dpi=1200)
