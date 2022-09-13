"""Tests the trace module.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""

import numpy as np
import pytest

from src.core.trace import Trace
from src.utils import Config, Exceptionable, SetupMode

excepter = Exceptionable(SetupMode.NEW)


@pytest.fixture
def basic_trace():
    """Create a generic trace.

    :return: Trace object.
    """
    points = [(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (2.0, -1.0), (0.0, 0.0)]
    return Trace(points, excepter.configs[Config.EXCEPTIONS.value])


def test_shift(basic_trace):
    """Test shifting a trace.

    :param basic_trace: Generic trace.
    """
    basic_trace.shift(vector=[1, 1, 0])
    assert np.array_equal(
        basic_trace.points, [(1.0, 1.0, 0.0), (1.0, 2.0, 0.0), (2.0, 2.0, 0.0), (3.0, 0.0, 0.0), (1.0, 1.0, 0.0)]
    )


def test_append(basic_trace):
    """Test appending a point to the trace coordinates.

    :param basic_trace: Generic trace.
    """
    basic_trace.append([1, 1, 0])
    assert np.array_equal(
        basic_trace.points,
        [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 1.0, 0.0), (2.0, -1.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
    )
