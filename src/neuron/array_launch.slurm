#!/bin/bash
#SBATCH --partition=wmglab
#SBATCH --mem=8000
#SBATCH --cpus-per-task=1
start_path_base=$1
bash ${start_path_base}${SLURM_ARRAY_TASK_ID}.sh