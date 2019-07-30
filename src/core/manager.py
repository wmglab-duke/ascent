from src.utils import *


class Manager(Exceptionable, Configurable):

    def __init__(self, master_config: dict, exception_config: list):

        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self, SetupMode.OLD, master_config)

