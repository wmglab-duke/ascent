#!/usr/bin/env python3.7
# builtins
# packages
# access
from src.utils import *

class Cuff(Exceptionable):
    """
    """

    def __init__(self, exception_config):
        # set up superclass
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)