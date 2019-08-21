# builtins
# packages
# access
from src.utils import *


class FEMManager(Exceptionable, Configurable, Saveable):

    def __init__(self, master_config: dict, exception_config: list)
        """
        :param master_config: preloaded configuration data for master
        :param exception_config: preloaded configuration data for exceptions
        """

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self, SetupMode.OLD, ConfigKey.MASTER, master_config)

        # Initialize FEMs
        self.fems: List[FEM] = []
