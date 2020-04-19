#!/usr/bin/env python3.7

# builtins
import json
import sys
import time

# access
from src.core import MockSample
from src.utils import *

start = time.time()

if len(sys.argv) != 2:
    print('INVALID number of arguments to mock_morphology_generator.py')
    exit(1)

exceptions_file = os.path.join('config', 'system', 'exceptions.json')

with open(exceptions_file, "r") as handle:
    exceptions_config: dict = json.load(handle)

# load mock sample configuration
mock_config = os.path.join('config', 'user', 'mock_samples', '{}.json'.format(sys.argv[1]))
mock_sample = MockSample(exceptions_config)
mock_sample.add(SetupMode.NEW, Config.MOCK_SAMPLE, mock_config)
mock_sample.make_nerve()
mock_sample.make_fascicles()
mock_sample.make_masks()

# END timer
end = time.time()
print('\nruntime: {}'.format(end - start))

# cleanup for console viewing/inspecting
del start, end
