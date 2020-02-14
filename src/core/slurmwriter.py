#!/bin/bash
#
#SBATCH --output=/hpc/home/wmglab/edm23/jobs/SparcSim2010/Data/Outputs/SparcSim2010.out
#SBATCH --job-name=SparcSim2010
#SBATCH --error=/hpc/home/wmglab/edm23/jobs/SparcSim2010/Data/Outputs/SparcSim2010.err
#SBATCH -p wmglab
#SBATCH --ntasks=36
#SBATCH --cpus-per-task=1

cd ~/jobs/SparcSim2010
cp -p ../MOD_Files/x86_64/special .
chmod a+rwx special
echo $SLURM_NTASKS

mpirun -np $SLURM_NTASKS ./special -mpi LaunchSim2010.hoc