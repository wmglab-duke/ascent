from typing import Union

from src.core import Sample, Simulation
from src.utils import *


class Query(Exceptionable, Configurable, Saveable):
    """
    IMPORTANT: MUST BE RUN FROM PROJECT LEVEL
    """

    def __init__(self, criteria_path: str):
        """
        :param exceptions_config:
        """

        # set up superclasses
        Configurable.__init__(self)
        Exceptionable.__init__(self, SetupMode.NEW)

        self._ran: bool = False  # marker will be set to True one self.run() is called (as is successful)
        self.add(SetupMode.NEW, Config.CRITERIA, criteria_path)  # initialize criteria

    def run(self):
        """
        Build query result using criteria
        :return: result as a dict
        """

        # preliminarily find sample, model, and sim filter indices if applicable (else None)
        sample_indices = self.search(Config.CRITERIA, 'indices', 'sample')
        model_indices = self.search(Config.CRITERIA, 'indices', 'model')
        sim_indices = self.search(Config.CRITERIA, 'indices', 'sim')

        sample_criteria = self.search(Config.CRITERIA, 'sample')
        model_criteria = self.search(Config.CRITERIA, 'model')
        sim_criteria = self.search(Config.CRITERIA, 'sim')

        samples_dir = 'samples'
        for sample in os.listdir(samples_dir):
            # skip this sample if applicable
            if sample_indices is not None and int(sample) not in sample_indices:
                continue

            # FILTER SAMPLE LEVEL HERE

            models_dir = os.path.join(samples_dir, sample, 'models')
            for model in os.listdir(models_dir):
                if model_indices is not None and int(model) not in model_indices:
                    continue

                # FILTER MODEL LEVEL HERE

                sims_dir = os.path.join(models_dir, model, 'sims')
                for sim in os.listdir(sims_dir):
                    if sim_indices is not None and int(sim) not in sim_indices:
                        continue




    def summary(self) -> dict:
        """

        :return:
        """

    def fetch_config(self) -> dict:
        """

        :return:
        """

    def fetch_object(self) -> Union[Sample, Simulation]:
        """

        :return:
        """



