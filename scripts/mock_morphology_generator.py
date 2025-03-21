#!/usr/bin/env python3.7

"""Generate mock sample morphology.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""

import os
import time
import warnings

from src.core import MockSample
from src.utils import Config, Configurable, SetupMode


def run(args):
    """Generate a mock sample morphology.

    :param args: The command line arguments.
    """
    warnings.warn(
        "There is a known issue where the mock morphology generator will create \
        nerve morphologies with areas slightly smaller than requested. A fix is in progress.",
        stacklevel=2,
    )
    start = time.time()

    # load mock sample configuration
    mock_config = os.path.join('config', 'user', 'mock_samples', f'{args.mock_sample_index}.json')
    mock_sample = MockSample()
    mock_sample.add(SetupMode.NEW, Config.MOCK_SAMPLE, mock_config).make_nerve().make_fascicles().make_masks()

    Configurable.write(mock_sample.configs['mock_sample'], mock_config)

    # END timer
    end = time.time()
    print(f'\nruntime: {end - start}')

    # cleanup for console viewing/inspecting
    del start, end
