#!/bin/bash

#SBATCH -c 1
#SBATCH --mem=64000
#SBATCH -t 72:0:0
#SBATCH -o runpipe_physcor_retcomp.o
#SBATCH -e runpipe_physcor_retcomp.e

module load anaconda/3.5.3
module load afni
module load fsl
module load freesurfer
export MNI152=$FSLDIR/data/standard/MNI152_T1_2mm_brain
module load anaconda/3.5.3 # looks like need to load twice for the libraries such as numpy to be loaded also.

python pipe.py --subjects ~/data/healthyvolunteer/fepi_subjects_physcor_checked_physio_skullstrip_reorient_connseedcordinates_aseg_registrations_connseed.txt --fixed ~/data/healthyvolunteer/processed/pipe_physcor_const_withmotreg.txt --fixed ~/data/healthyvolunteer/processed/pipe_physcor_retcomp.txt --template $MNI152 --meants --seedconn --resout ~/data/healthyvolunteer/processed/physcor/pipe_physcor_retcomp_withmotreg --fixpipename retcomp_withmotreg --keepintermed




