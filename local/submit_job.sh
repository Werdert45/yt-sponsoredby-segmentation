#!/bin/bash

#SBATCH --account=3214046
#SBATCH --partition=dsba
#SBATCH --gpus=1
#SBATCH --mem=10G
#SBATCH --job-name="check of db" 
#SBATCH --time=00:01:00
#SBATCH --output=/home/3214046/my_dir/output/%x_%j.out
#SBATCH --error=/home/3214046/my_dir/error/%x_%j.err

python3 /home/3214046/my_dir/check.py
