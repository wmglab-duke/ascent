import json
import os
from src.utils.enums import SetupMode, Config
from matplotlib import pyplot as plt

from src.core import Waveform


def load(config_path: str):
    """
    Loads in json data and returns to user, assuming it has already been validated.
    :param config_path: the string path to load up
    :return: json data (usually dict or list)
    """
    with open(config_path, "r") as handle:
        # print('load "{}" --> key "{}"'.format(config, key))
        return json.load(handle)


exceptions_config = load(os.path.join('../config', 'system', 'exceptions.json'))
model_config = load(os.path.join('plotting_models', 'model0.json'))
sim_config = load(os.path.join('plotting_sims', 'sim1.json'))

waveform = Waveform(exceptions_config)
waveform.add(SetupMode.OLD, Config.MODEL, model_config)
waveform.add(SetupMode.OLD, Config.SIM, sim_config)
waveform.init_post_config()
waveform.generate()
waveform.plot()

figure1 = plt.figure(1)
plt.plot(waveform.wave, 'k-')
plt.show()
figure1.savefig('C:\\Users\\edm23\\Desktop\\pipeline_figures\\waveform_examples\\sinusoid.svg', format='svg', dpi=1200)


