from typing import List

from src.core import Slide, Map
from src.utils import *


class Manager(Exceptionable, Configurable):

    def __init__(self, master_config: dict, exception_config: list, map: Map):

        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self, SetupMode.OLD, master_config)

        self.slides: List[Slide] = []

        self.map = map
