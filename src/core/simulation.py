from core import Sample
from utils import Exceptionable, Configurable, Saveable, SetupMode


class Simulation(Exceptionable, Configurable, Saveable):

    def __init__(self, sample: Sample, exception_config: list):

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

    def resolve_product(self):
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

