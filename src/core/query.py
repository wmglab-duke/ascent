from typing import Union

from src.core import Sample, Simulation
from src.utils import *


class Query(Exceptionable, Configurable, Saveable):
    """

    """

    def __init__(self, exceptions_path: str, project_path: str, criteria_path: str):
        """

        :param exceptions_config:
        """

        # set up superclasses
        Configurable.__init__(self)
        Exceptionable.__init__(self, SetupMode.NEW, exceptions_path)

        # initialize
        self.project_path = project_path  # for locating the samples directory
        self._ran: bool = False  # marker will be set to True one self.run() is called (as is successful)
        self._load_criteria(criteria_path)  # initialize criteria

    def _load_criteria(self, path: str):
        """
        Get JSON data for query criteria from given path
        :param path: path to JSON file
        :return: dict with JSON data
        """

        if (not os.path.isfile(path)) or ('.json' not in path):
            self.throw(52)

        self.add(SetupMode.NEW, Config.CRITERIA, self.load(path))

    def run(self):
        """
        Build query result using criteria
        :return: result as a dict
        """

        search_root: str = os.path.join(self.project_path, 'samples')

        for sample_dir in os.listdir(search_root):



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



