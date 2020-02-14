#!/bin/bash
#SBATCH --job-name=Batch1
#SBATCH --output=SPARC.out
#SBATCH --error=SPARC.err
#SBATCH --mem=8000
#SBATCH -c 1

StartSim=125
EndSim=130
for sim in `seq $StartSim $EndSim`; do
	fname="ImTheraSim${sim}/StartSim${sim}.slurm"
	sbatch $fname
done
