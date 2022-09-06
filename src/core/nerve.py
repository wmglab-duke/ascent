#!/usr/bin/env python3.7

"""Defines Nerve class.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""


from src.core import Trace
from src.utils import Config


class Nerve(Trace):
    """The Nerve class is a subclass of the Trace class, used to represent the epineurium boundary."""

    def __init__(self, trace: Trace):
        """Initialize a Nerve object.

        :param trace: Trace object to be converted to a Nerve object.
        """
        Trace.__init__(self, trace.points, trace.configs[Config.EXCEPTIONS.value])

    def morphology_data(self):
        """Return the morphology data of the Nerve object."""
        return {"area": self.area()}
