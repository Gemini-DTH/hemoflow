#!/bin/bash
#SBATCH --ntasks=30

#SBATCH -p plgrid

#SBATCH -A {{ grant_id }}

module load hdf5
module load cmake

{% stage_in config %}
{% stage_in flowrate %}
{% stage_in vox %}

mkdir build
cd build
cmake
make -j 10

mpirun -n 30 ./hemoFlow ../NAP_122_L01_F03_PA64_5_CFD.xml
