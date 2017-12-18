#!/bin/bash

#SBATCH -c 8
#SBATCH --mem=128000
#SBATCH -t 72:0:0
#SBATCH -o runpipe_physcor_nophyscor_more.o
#SBATCH -e runpipe_physcor_nophyscor_more.e

module load anaconda/3.5.3
module load afni
module load fsl
module load freesurfer
export MNI152=$FSLDIR/data/standard/MNI152_T1_2mm_brain
module load anaconda/3.5.3 # looks like need to load twice for the libraries such as numpy to be loaded also.

python pipe.py --subjects ~/data/healthyvolunteer/fepi_subjects_physcor_more_checked_aseg_fsrecon_physio_reorient_connseedLRprimarymotor_Raichlenetal2016.txt --pipeline ~/data/healthyvolunteer/processed/pipe_physcor_const_withmotreg.txt --template $MNI152 --meants --seedconn --tomni --keepintermed --outputsubjects /global/home/hpc3820/data/healthyvolunteer/processed/physcor/proc_nophyscor_st_mc_censor_motreg_be_ssmooth_hpf.sbj



