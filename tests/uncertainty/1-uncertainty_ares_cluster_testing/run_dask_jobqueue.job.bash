#!/bin/bash -l
#SBATCH -J easyvvuq_hemoflow
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH --time=08:00:00
#SBATCH --mem=8GB
#SBATCH -A plggemini2026-cpu
#SBATCH -p plgrid-services
#SBATCH --output=./slurm-%j.out
#SBATCH --error=./slurm-%j.err

# Finish with error on first command with error
set -e

## Change to the directory where sbatch was called
cd $TMPDIR
pwd

## Load modules
echo "Loading modules"
module load python/3.12.3
module load miniconda3/24.5

## Clone required repo with scripts
echo "Cloning repo"
git clone https://github.com/Gemini-DTH/hemoflow.git 
git checkout feature-aneurysm branch

cd $TMPDIR
mkdir env_mountpoint
squashfuse $SCRATCH/lbmpost.squashfs env_mountpoint
conda activate $TMPDIR/env_mountpoint

cp /net/pr2/projects/plgrid/plgggemini/Hemoflow/LBMpost-fix-vvuq_output_format.zip .
unzip LBMpost-fix-vvuq_output_format.zip

## Run
echo "Running simulation"
export HEMOFLOW_PATH=/net/pr2/projects/plgrid/plgggemini/Hemoflow/hemoflow/build/hemoFlow
export LBMPOST_PATH=$TMPDIR/LBMpost-fix-vvuq_output_format/main.py
export JOBS_NUM=2 #number of parallel jobs (workers) to submit to the cluster queue.

cd $TMPDIR/hemoflow/tests/uncertainty/1-uncertainty_ares_cluster_testing
python3 -u ./uncertainty_quantification_test.py --slurm=dask-jobqueue # running easyvvuq experiment using dask-jobqueue SLURMCluster

echo "Finish"