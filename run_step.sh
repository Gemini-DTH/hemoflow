#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=30
#SBATCH --time=01:00:00


#SBATCH -p plgrid

#SBATCH -A {{ grant_id }}

set -e

module load hdf5

cd $SCRATCH/hemoflow

{% stage_in NAP_122_L01_F03_PA64_5_CFD.xml %} # config file
{% stage_in cerebral_flowrate.txt %}
{% stage_in vox_NAP_122_L01_F03_PA64_5c.npz %}

cd build

mpirun -n 30 ./hemoFlow ../NAP_122_L01_F03_PA64_5_CFD.xml
