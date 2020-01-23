import itertools

from src.core import Sample
from src.utils import Exceptionable, Configurable, Saveable, SetupMode, Config


class Simulation(Exceptionable, Configurable, Saveable):

    def __init__(self, sample: Sample, exception_config: list):

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

        self.factors = dict()

    def resolve_factors(self):

        if len(self.factors.items()) > 0:
            self.factors = dict()

        def search(dictionary, remaining_n_dims):
            if remaining_n_dims < 1:
                return
            for key, value in dictionary.items():
                if type(value) == list and len(value) > 1:
                    self.factors[key] = value
                    remaining_n_dims -= 1
                elif type(value) == dict:
                    search(value, remaining_n_dims)

        loopable = ['fibers', 'waveform']
        search(
            {key: value for key, value in self.configs[Config.SIM.value].items() if key in loopable},
            self.search(Config.SIM, "n_dimensions")
        )

        return self

    def write_waveforms(self):  # , factors, product
        # factors list of dictionaries, each has name and value (which has a length)
        # within extracellular stim, if key in factors:
        #     do

        print("within write_waveforms")
        print(self.factors)



    def fiber_xy_coordinates(self):
        pass

    def fiber_z_coordinates(self):
        pass

    def save_coordinates(self):
        pass

    ############################

    def build_sims(self):
        pass
        print("here")
        # loop cartesian product
        # build_file_structure()
        # build_hoc()
        # copy_trees()

    def _build_file_structure(self):
        pass

    def _copy_trees(self, trees=None):
        if trees is None:
            trees = ['Ve_data', 'waveforms']

    def _build_hoc(self):
        pass
