# builtins

# packages

# SPARCpy
from .slide_manager import SlideManager
from src.utils import *


class ModelManager(Exceptionable, Configurable, Saveable):

    def __init__(self, slide_manager: SlideManager, master_config: dict, exception_config: list):

        # Initializes superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)
        Configurable.__init__(self, SetupMode.OLD, ConfigKey.MASTER, master_config)