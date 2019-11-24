#!/usr/bin/env python3.7

# access
from src.core import Trace
from src.utils import Config


class Nerve(Trace):

    def __init__(self, trace: Trace):
        Trace.__init__(self, trace.points, trace.configs[Config.EXCEPTIONS.value])

    def morphology_data(self):
        return {"length_unit": "micrometer", "area": self.area()}
