from src.utils import Exceptionable, Configurable, SetupMode, ConfigKey


class Waveform(Exceptionable, Configurable):

    def __init__(self, master_config: dict, exceptions_config: list):

        # set up supclasses
        Configurable.__init__(self, SetupMode.OLD, ConfigKey.MASTER, master_config)
        Exceptionable.__init__(self, SetupMode.OLD, exceptions_config)

        # get mode
        modes = self.search_multi_mode()

        # get global vars data
        global_vars = self.search()

        # unpack global vars

