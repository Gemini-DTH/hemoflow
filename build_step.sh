#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:30:00

#SBATCH -p plgrid-testing

#SBATCH -A {{ grant_id }}

cd $SCRATCH
pwd

module load hdf5
module load cmake

if [[ -d "hemoflow" ]]
then
    echo "hemoflow directory exists on your scratch."
else
    ## Clone repository and switch into selected revision
    echo Preparing computation source code
    {% clone_repo %}
fi

cd hemoflow

mkdir build
cd ./build
cmake ..
make -j 10
