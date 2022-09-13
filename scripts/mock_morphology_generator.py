#!/usr/bin/env python3.7

"""Generate mock sample morphology.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""


import json
import os
import time

from src.core import MockSample
from src.utils import Config, SetupMode, TemplateOutput


def run(args):
    """Generate a mock sample morphology.

    :param args: The command line arguments.
    """
    start = time.time()

    exceptions_file = os.path.join('config', 'system', 'exceptions.json')

    with open(exceptions_file, "r") as handle:
        exceptions_config: dict = json.load(handle)

    # load mock sample configuration
    mock_config = os.path.join('config', 'user', 'mock_samples', f'{args.mock_sample_index}.json')
    mock_sample = MockSample(exceptions_config)
    mock_sample.add(SetupMode.NEW, Config.MOCK_SAMPLE, mock_config).make_nerve().make_fascicles().make_masks()

    TemplateOutput.write(mock_sample.configs['mock_sample'], mock_config)

    # END timer
    end = time.time()
    print(f'\nruntime: {end - start}')

    # cleanup for console viewing/inspecting
    del start, end
