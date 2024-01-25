#!/usr/bin/env python3.7

"""Import the transmembrane current matrix.

This script will likely later become part of the query class later on,
and serves as a starting point for template generation.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent.
"""
import os
import struct

import numpy as np


def import_tm_current_matrix(imembrane_file_name):
    """Extract current amplitude, number of axons, time vector, and transmembrane current matrix from a binary file.

    :param imembrane_file_name: file containing full current matrix and starting metadata.
    :return: current_amp: amplitude of current
    :return: time_vector: time points correlating with transmembrane currents
    :return: current_matrix: transmembrane current matrix
    """
    with open(imembrane_file_name, 'rb') as file:
        alldata = file.read()
        # TODO: check that the format '@' works on other machines. Test on cluster.
        # Currently it is in native format, might need to be in standard format.
        _, _, tstop, _, _, dt, _, _, axon_num, vector_size, _ = struct.unpack(
            "@iidiidiidii", alldata[:56]  # 56 is the total number of bytes correlating with the format
        )
        current_matrix = np.array(struct.unpack_from(f"{vector_size}d", alldata[56:]))
    file.close()

    # Build current matrix and time vectors from file data
    current_matrix = current_matrix.reshape(
        ((int)(vector_size / axon_num), -1), order='F'
    )  # Matlab and Fortran ('F order') both use column-major layout as the default
    time_vector = np.arange(0, dt * (vector_size / axon_num), dt)

    return tstop, time_vector, current_matrix


# Test on sample file
sample = 20230323
model = 0
sim = 20230323092
n_sim = 0
axon = 0
fiber = 0
amp_num = 0
file = os.path.join(
    os.getcwd(),
    "samples",
    f'{sample}',
    "models",
    f'{model}',
    "sims",
    f'{sim}',
    "n_sims",
    f'{n_sim}',
    "data",
    "outputs",
    f"Imembrane_axon{axon}_fiber{fiber}_amp{amp_num}.dat",
)
import_tm_current_matrix(file)
