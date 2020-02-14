#
# DataManager.getThresholds(sample, fiber_diam, waveform, fiber_locs) -> List[Thresholds]
#
# DataManager.getRecruitment(sample, fiber_diam, waveform, percent_act) -> e.g., I20
#
# DataManager.getDistanceFromContact(sample, fibers) -> List[Distances]
#
# NOT FOR DATA MANAGER; FOR LATER ANALYSIS EXAMPLE CODE
# DataManager.plotLegend(samples) -> List[Colors], Figure Legend
#
# DataManager.plotHeatMap(sample, fiber_diam, waveform)
#
# DataManager.plotSexDiff(List [samples], )
#

from typing import List

from src.utils import Configurable, Exceptionable, SetupMode


class DataManager(Exceptionable, Configurable):

    def __init__(self, runs: List[dict]):
        """
        Initializer; load in all required objects, as  specified by the run configurations (runs)
        :param runs:
        """
        Configurable.__init__(self)
        Exceptionable.__init__(self, SetupMode.NEW)

        # self.data: Dict[int, Dict[str, Union[Sample, Dict]]]