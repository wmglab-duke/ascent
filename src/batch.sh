#!/bin/bash

module load Neuron/7.6.2
chmod +x batch.py
./batch.py "$@"
