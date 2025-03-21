#!/bin/bash

# The copyrights of this software are owned by Duke University.
# Please refer to the LICENSE and README.md files for licensing instructions.
# The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent

unset DISPLAY
start_path_base=$1
bash ${start_path_base}${SLURM_ARRAY_TASK_ID}.sh
