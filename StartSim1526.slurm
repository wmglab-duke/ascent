#!/bin/bash
#
#SBATCH --output=/hpc/home/edm23/LivaNova/SparcSim1526/Data/Outputs/SparcSim1526.out
#SBATCH --job-name=SparcSim1526
#SBATCH --error=/hpc/home/edm23/LivaNova/SparcSim1526/Data/Outputs/SparcSim1526.err
#SBATCH -p wmglab
#SBATCH --ntasks=377
#SBATCH --cpus-per-task=1

cd ~/LivaNova/SparcSim1526	
cp -p ../MOD_Files/x86_64/special .
chmod a+rwx special
echo $SLURM_NTASKS

mpirun -np $SLURM_NTASKS ./special -mpi LaunchSim1526.hoc



