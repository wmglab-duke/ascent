#!/bin/bash

<<comment
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE.txt and README.txt files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
comment

module load Neuron/7.6.2
python3 submit.py "$@"
