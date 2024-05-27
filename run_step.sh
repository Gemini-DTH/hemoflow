#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=30
#SBATCH --time=00:40:00

#SBATCH -p plgrid

#SBATCH -A {{ grant_id }}

set -e

module load hdf5
module load cmake

cd $SCRATCH
pwd

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

cd $SCRATCHDIR

cp -r $SCRATCH/hemoflow/test_cases/run/. .

mpirun -n 30 $SCRATCH/hemoflow/build/hemoFlow ./NAP_122_L01_F03_PA64_5_CFD.xml

cd output_*

ls -la

{% stage_out *.dat %}
{% stage_out *.vti %}
