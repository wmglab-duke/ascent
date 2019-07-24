#!/usr/bin/env python3.7

"""
File:       Slide.py
Author:     Jake Cariello
Created:    July 24, 2019

Description:

    OVERVIEW

    INITIALIZER

    PROPERTIES

    METHODS

"""
from typing import List

# really weird syntax is required to directly import the class without going through the pesky init
from .Fascicle import Fascicle
from .Nerve import Nerve
from src.utils import *


class Slide(Exceptionable, Configurable):

    def __init__(self, fascicles: List[Fascicle], nerve: Nerve, master_config: dict, exception_config: list):

        # init superclasses
        Configurable.__init__(self, SetupMode.OLD, ConfigKey.MASTER, master_config)
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

        self.nerve = nerve
        self.fascicles = fascicles
