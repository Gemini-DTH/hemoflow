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
    cd hemoflow
    git pull
else
    ## Clone repository and switch into selected revision
    echo Preparing computation source code
    {% clone_repo %}
    cd hemoflow
fi

if [[ -d "build" ]]
then
    echo "Build dir already exists."
else
    mkdir build

fi
cd ./build

cmake ..
make -j 10
