from src.core import *
from src.utils import *
import cv2


class Runner(Exceptionable, Configurable):

    def __init__(self, config_file_path: str):

        # initialize Configurable super class
        Configurable.__init__(self, SetupMode.NEW, ConfigKey.MASTER, config_file_path)

        # get config path info from config and set to class vars
        self.exceptions_config_path = self.path(ConfigKey.MASTER, 'config_paths', 'exceptions')

        # initialize Exceptionable super class
        Exceptionable.__init__(self, SetupMode.NEW, self.exceptions_config_path)

    def run(self):
        # _ = SlideMap(self.configs[ConfigKey.MASTER.value], self.configs[ConfigKey.EXCEPTIONS.value])

        self.trace = Trace([[0,  0, 0],
                            [1,  0, 0],
                            [6,  0, 0],
                            [2,  1, 0],
                            [2,  2, 0],
                            [1,  2, 0],
                            [0,  2, 0],
                            [0,  1, 0]], self.configs[ConfigKey.EXCEPTIONS.value])
        # TEST: exceptions configuration path
        # print('exceptions_config_path:\t{}'.format(self.exceptions_config_path))

        # TEST: retrieve data from config file
        # print(self.search(ConfigKey.MASTER, 'test_array', 0, 'test'))

        # TEST: throw error
        # self.throw(2)

    def test1(self):

        path = 'D:/Documents/SPARCpy/data/tracefile2.tif'
        img = cv2.imread(path, -1)

        cv2.utils.dumpInputArray(img)

        cnts, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    def test2(self):

        path = '/Users/jakecariello/Box/SPARCpy/data/tracefile2.tif'
        img = cv2.imread(path, -1)

        cv2.utils.dumpInputArray(img)

        self.cnts, self.hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
