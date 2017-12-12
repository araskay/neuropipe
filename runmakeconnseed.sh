#!/bin/bash

#SBATCH -J runmakeconnseed
#SBATCH -c 1
#SBATCH --mem=64000
#SBATCH -t 12:0:0
#SBATCH -o runmakeconnseed.o
#SBATCH -e runmakeconnseed.e

module load anaconda/3.5.3
module load afni
module load fsl
module load freesurfer
export MNI152=$FSLDIR/data/standard/MNI152_T1_2mm_brain
module load anaconda/3.5.3 # looks like need to load twice for the libraries such as numpy to be loaded also.

python makeconnseed.py --input ~/data/healthyvolunteer/fepi_subjects_physcor_more_checked_aseg_fsrecon_physio_reorient.txt --output ~/data/healthyvolunteer/fepi_subjects_physcor_more_checked_aseg_fsrecon_physio_reorient_connseedLRprimarymotor_Raichlenetal2016.txt --seed ~/data/atlas/LRprimarymotor_Raichlenetal2016.nii.gz --template $MNI152 --binary --boldregdof 6 --pipeline ~/data/healthyvolunteer/processed/pipeline_noRet.txt
