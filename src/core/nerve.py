#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""


from src.core import Trace
from src.utils import Config


class Nerve(Trace):
    def __init__(self, trace: Trace):
        Trace.__init__(self, trace.points, trace.configs[Config.EXCEPTIONS.value])

    def morphology_data(self):
        return {"area": self.area()}
