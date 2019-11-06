#!/usr/bin/env python3.7

# access
from src.core import Trace
from src.utils import ConfigKey


class Nerve(Trace):

    def __init__(self, trace: Trace):
        Trace.__init__(self, trace.points, trace.configs[ConfigKey.EXCEPTIONS.value])

    def output_morphology_data(self):
        nerve = {"area": self.area()}

        return {"length_unit": "micrometer", "area": nerve}