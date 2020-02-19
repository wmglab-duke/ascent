#!/bin/bash
#SBATCH --job-name=Batch1
#SBATCH --output=SPARC.out
#SBATCH --error=SPARC.err
#SBATCH --mem=8000
#SBATCH -p wmglab
#SBATCH -c 1

model_num=101
StartSim=1
EndSim=6
for sim in `seq $StartSim $EndSim`; do
	fname="SPARC_UWM${model_num}_SL_${sim}/StartSim${sim}.slurm"
	sbatch $fname
done
