import os
from src.core import *
from src.utils import *


class Runner(Exceptionable, Configurable):

    def __init__(self, config_file_path: str):

        # initialize Configurable super class
        Configurable.__init__(self, config_file_path)

        # get config path info from config and set to class vars
        self.exceptions_config_path = self.path_get('config_paths', 'exceptions')
        self.slide_map_config_path = self.path_get('config_paths', 'slide_map')

        # initialize Exceptionable super class
        Exceptionable.__init__(self, self.exceptions_config_path)

    def run(self):
        _ = SlideMap(self.slide_map_config_path, self.exceptions_config_path)

        # quick sanity check
        print('exceptions_config_path:\t{}'.format(self.exceptions_config_path))
        print('slide_map_config_path:\t{}'.format(self.slide_map_config_path))

        print(self.get('test_array', 0, 'test'))
        self.throw(2)
