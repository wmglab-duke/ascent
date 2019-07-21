from src.core import *
from src.utils import *


class Runner(Exceptionable, Configurable):

    def __init__(self, config_file_path: str):

        # initialize Configurable super class
        Configurable.__init__(self, config_file_path)

        # get config path info from config and set to class vars
        self.config_paths: dict = self.config.get('config_paths')
        self.exceptions_config_path = self.__build_config_path('exceptions')
        self.slide_map_config_path = self.__build_config_path('slide_map')

        # initialize Exceptionable super class
        Exceptionable.__init__(self, self.exceptions_config_path)

    def __build_config_path(self, desired):
        """
        :param desired: desired type of configuration file
        :return: system-specific path for the desired configuration file
        """
        return os.path.join(self.config_paths.get('root'), self.config_paths.get(desired))

    def run(self):
        _ = SlideMap(self.slide_map_config_path, self.exceptions_config_path)
