#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=30
#SBATCH --time=00:40:00

#SBATCH -p plgrid

#SBATCH -A {{ grant_id }}

set -e

module load hdf5
module load cmake

cd $SCRATCHDIR

cp -r $SCRATCH/hemoflow/test_cases/run/. .

mpirun -n 30 $SCRATCH/hemoflow/build/hemoFlow ./NAP_122_L01_F03_PA64_5_CFD.xml

cd output_*

ls -la

{% stage_out hemoflow_output %}
