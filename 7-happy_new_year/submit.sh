#!/usr/bin/bash"
# Project/Account (use your own)
#SBATCH -A scw1701
#SBATCH --job-name=happy_new_year     # Job name
#SBATCH --output happy_new_year-%j.out     # Job name
#SBATCH --error happy_new_year-%j.err     # Job name
#
# We ask for 1 tasks with 1 core only.
# We ask for a GPU
#SBATCH -p gpu_v100
#SBATCH --gres=gpu:2
#SBATCH --mail-user=f.vidal@bangor.ac.uk
#
# Number of tasks per node
#SBATCH --ntasks-per-node=1
#
# Number of cores per task
#SBATCH --cpus-per-task=1
#
# Use one node
#SBATCH --nodes=1
#
# Runtime of this jobs is less than 5 hours.
#SBATCH --time=48:00:00
module purge > /dev/null 2>&1
module load cmake compiler/gnu/8/1.0 compiler/gnu/8/1.0 CUDA python/3.7.0

export EGL_PLATFORM=
export PYTHONPATH=$HOME/gvirtualxray-install/gvxrWrapper-1.0.4/python3:$PYTHONPATH

python3 HappyNewYear.py
