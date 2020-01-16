import itertools

from core import Sample
from utils import Exceptionable, Configurable, Saveable, SetupMode, Config


class Simulation(Exceptionable, Configurable, Saveable):

    def __init__(self, sample: Sample, exception_config: list):

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

    def resolve_product(self):
        n_dimensions = self.search(Config.SIM, "n_dimensions")
        # ONE fibers type, list with diff parameters
        # ONE waveforms type, list with diff parameters

        factors: dict

        def recursive_search(n_dimensions_remaining, current_search_dictionary):
            pass
        #
        # # loop through all keys, for each key, check if value is a list
        # if a list, check for number of values.
        #     if greater than one, add key/path to dimensions
        # if counter dimensions == n_dimensions break out
        # if current value of key is type dictionary, then recursively go through dictionary
        # itertools.product([1,2,3], ['a','b'], [4,5])

        pass

    def write_waveforms(self):
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

    def _copy_trees(self, trees = None):
        if trees is None:
            trees = ['Ve_data', 'waveforms']

    def _build_hoc(self):
        pass

