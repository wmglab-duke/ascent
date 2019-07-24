"""
File:       nerve.py
Author:     Jake Cariello
Created:    July 24, 2019

Description: Proxy class for a single trace (might expand later??)

"""

from src.core import Trace
from src.utils import ConfigKey


class Nerve(Trace):

    def __init__(self, trace: Trace):
        Trace.__init__(self, trace.points, trace.configs[ConfigKey.EXCEPTIONS.value])