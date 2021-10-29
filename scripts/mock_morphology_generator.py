#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE.txt and README.txt files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

# builtins
import json
import sys
import time

# access
from src.core import MockSample
from src.utils import *


def run(args):
    start = time.time()
    
    exceptions_file = os.path.join('config', 'system', 'exceptions.json')

    with open(exceptions_file, "r") as handle:
        exceptions_config: dict = json.load(handle)

    # load mock sample configuration
    mock_config = os.path.join('config', 'user', 'mock_samples', '{}.json'.format(args.mock_sample_index))
    mock_sample = MockSample(exceptions_config)
    mock_sample.add(SetupMode.NEW, Config.MOCK_SAMPLE, mock_config) \
        .make_nerve() \
        .make_fascicles() \
        .make_masks()

    # END timer
    end = time.time()
    print('\nruntime: {}'.format(end - start))

    # cleanup for console viewing/inspecting
    del start, end
