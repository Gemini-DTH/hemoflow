#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=30
#SBATCH --time=02:00:00

#SBATCH -p plgrid

#SBATCH -A {{ grant_id }}

set -e

module load hdf5
module load cmake

cd $SCRATCH/hemoflow/test_cases/run

mpirun -n 30 $SCRATCH/hemoflow/build/hemoFlow ./NAP_122_L01_F03_PA64_5_CFD.xml

cd output_*

{% stage_out hemoflow_output %}
