from src.core import Sample
from src.utils import Exceptionable, Configurable, Saveable, SetupMode, Config


class Simulation(Exceptionable, Configurable, Saveable):

    def __init__(self, sample: Sample, exception_config: list):

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

        self.sample = sample
        self.factors = dict()
        self.products = dict()

    def resolve_factors(self):
        if len(self.factors.items()) > 0:
            self.factors = dict()

        def search(dictionary, remaining_n_dims, sub):
            print(sub)
            if remaining_n_dims < 1:
                return
            for key, value in dictionary.items():
                if type(value) == list and len(value) > 1:
                    print('adding key {} to sub {}'.format(key, sub))
                    self.factors[sub][key] = value
                    remaining_n_dims -= 1
                elif type(value) == dict:
                    print('recurse: {}'.format(value))
                    search(value, remaining_n_dims, sub)

        for flag in ['fibers', 'waveform']:
            self.factors[flag] = dict()
            search(
                self.configs[Config.SIM.value][flag],
                self.search(Config.SIM, "n_dimensions"),
                flag
            )



    def write_fibers(self):
        pass

    def write_waveforms(self):
        # factors list of dictionaries, each has name and value (which has a length)
        # within extracellular stim, if key in factors:
        #     do
        pass

    def fiber_xy_coordinates(self):
        pass

    def fiber_z_coordinates(self):
        pass

    def save_coordinates(self):
        pass

    ############################

    def build_sims(self):
        pass
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
