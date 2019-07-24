"""
File:       Nerve.py
Author:     Jake Cariello
Created:    July 24, 2019

Description: Container class for a single trace (might expand later??)

"""

from src.core import Trace


class Nerve:

    def __init__(self, trace: Trace):
        self.trace = trace
