#!/bin/bash
#SBATCH --ntasks=10

#SBATCH -p plgrid

#SBATCH -A {{ grant_id }}

module load hdf5
module load cmake

mkdir build
cd build
cmake
make -j 10
