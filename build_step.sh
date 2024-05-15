#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:30:00

#SBATCH -p plgrid-testing

#SBATCH -A {{ grant_id }}

module load hdf5
module load cmake

mkdir build
cd ./build
cmake ..
make -j 10
