from core import Sample
from utils import Exceptionable, Configurable, Saveable, SetupMode


class Simulation(Exceptionable, Configurable, Saveable):

    def __init__(self, sample: Sample, exception_config: list):

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self)

    def fiber_xy_coordinates(self):
        pass

    def fiber_z_coordinates(self):
        pass

