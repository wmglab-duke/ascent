"""Tests the utils module.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""

import os
import pickle

import pytest

from src.utils import Configurable, Saveable

saver = Saveable()
configurator = Configurable()


def test_saveable():
    """Tests the Saveable class."""
    # test that save works
    saver.save('test.pkl')
    # test that load works
    with open('test.pkl', 'rb') as file:
        pickle.load(file)
    # test that save fails with bad path
    with pytest.raises(FileNotFoundError):
        saver.save('nonexistent_folder/bad_path.pkl')
    # test that load fails with bad path
    with pytest.raises(FileNotFoundError), open('bad_path', 'rb') as file:
        pickle.load(file)
    os.remove('test.pkl')


def test_configurable():
    """Tests the Configurable class."""
