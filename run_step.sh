#!/bin/bash
#SBATCH --ntasks=30

#SBATCH -p plgrid

#SBATCH -A {{ grant_id }}

module load hdf5

{% stage_in config %}
{% stage_in flowrate %}
{% stage_in vox %}

cd build

mpirun -n 30 ./hemoFlow ../NAP_122_L01_F03_PA64_5_CFD.xml
