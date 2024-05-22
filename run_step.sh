#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=30
#SBATCH --time=02:00:00


#SBATCH -p plgrid

#SBATCH -A {{ grant_id }}

set -e

module load hdf5
module load cmake

cd $SCRATCHDIR

{% stage_in_artifact NAP_122_L01_F03_PA64_5_CFD.xml %} # config file
{% stage_in_artifact cerebral_flowrate.txt %}
{% stage_in_artifact vox_NAP_122_L01_F03_PA64_5c.npz %}

mpirun $SCRATCH/hemoflow/build/hemoflow -n 30 ./NAP_122_L01_F03_PA64_5_CFD.xml
