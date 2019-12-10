from src.utils import *
from src.core import FiberManager, SlideManager


class SimulationBuilder(Exceptionable, Configurable, Saveable):
    def __init__(self, master_config: dict, exception_config: list, fm: FiberManager, sm: SlideManager):

        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self, SetupMode.OLD, Config.MASTER, master_config)

        self.master_path = 'SOME_PATH'
        self.fm = fm
        self.sm = sm


    def build_hoc(self):
        """
        Write file LaunchSim###.hoc
        :return:
        """
        pass

    def build_slurm(self):
        """
        Write file StartSim###.slurm
        :return:
        """
        pass
