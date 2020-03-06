from typing import Union

from core import Sample, Simulation
from src.utils import *


class Query(Exceptionable, Configurable, Saveable):
    """

    """

    def __init__(self, exceptions_config: list):
        """

        :param exceptions_config:
        """

        # set up superclasses
        Configurable.__init__(self)
        Exceptionable.__init__(self, SetupMode.OLD, exceptions_config)

        # initialize

    def set_query(self):
        """

        :return:
        """
        pass

    def run(self):
        """

        :return:
        """

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



