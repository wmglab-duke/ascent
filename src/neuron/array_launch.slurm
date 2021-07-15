#!/bin/bash

<<comment
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE.txt and README.txt files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
comment

#SBATCH --partition=wmglab
#SBATCH --mem=8000
#SBATCH --cpus-per-task=1
start_path_base=$1
bash ${start_path_base}${SLURM_ARRAY_TASK_ID}.sh