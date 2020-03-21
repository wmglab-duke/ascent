import json
import os
import pickle

from src.utils.enums import SetupMode, Config
from matplotlib import pyplot as plt

from src.core import FiberSet


def load(config_path: str):
    """
    Loads in json data and returns to user, assuming it has already been validated.
    :param config_path: the string path to load up
    :return: json data (usually dict or list)
    """
    with open(config_path, "r") as handle:
        # print('load "{}" --> key "{}"'.format(config, key))
        return json.load(handle)


def load_obj(path: str):
    return pickle.load(open(path, 'rb'))


sample_num = 24
sample_file = os.path.join(
    'plotting_samples',
    'sample{}_d.obj'.format(sample_num)
)

# instantiate sample
sample = load_obj(sample_file)

exceptions_config = load(os.path.join('../config', 'system', 'exceptions.json'))
model_config = load(os.path.join('plotting_models', 'model0.json'))
sim_config = load(os.path.join('plotting_sims', 'sim3.json'))

fiberset = FiberSet(sample, exceptions_config)
fiberset.add(SetupMode.OLD, Config.SIM, sim_config)
fiberset.add(SetupMode.OLD, Config.MODEL, model_config)
fiberset.generate()

left = -2000
right = 2000
up = 2000
down = -2000

figure1 = plt.figure(1)
for slide in sample.slides:
    slide.nerve.plot('k-')
    for fascicle in slide.fascicles:
        fascicle.outer.plot('k-')
        for inner in fascicle.inners:
            inner.plot('k-')

plt.axes().set_aspect('equal')
plt.xlim(left, right)
plt.ylim(down, up)


fibers_xy = fiberset._generate_xy()
for point in fibers_xy:
    plt.plot(point[0], point[1], 'r*')

plt.show()
figure1.savefig('C:\\Users\\edm23\\Desktop\\pipeline_figures\\fibers_xy_examples\\wheel.svg', format='svg', dpi=1200)


