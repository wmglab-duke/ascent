#!/usr/bin/env python3.7

# builtins

# packages

# access
from .cuff_model import CuffModel
from .nerve_model import NerveModel
from .cuff_fill_model import CuffFill
from .domain_model import Domain
from src.utils import *


class FEM(Exceptionable)

    def __init__(self, exception_config: list):
        """
        :param exception_config: pre-loaded configuration data
        """

        # will need to input paths to sectionwise files somehow
        # will need to load parameters for electrode
        # will need to load generic FEM parameters (ground length, ground radius, region of higher mesh)

        # init superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

    def cuff_validation():
        """
        Checks to make sure that the chose cuff geometry does not conflict with itself, the nerve, or distant ground
        :return: Boolean for True (no intersection) or False (issues with geometry overlap)
        """
