#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -M hpc3820@localhost
#$ -o /home/hpc3820/code/pipeline/runmakeconnseed_output.txt
#$ -e /home/hpc3820/code/pipeline/runmakeconnseed_error.txt
use anaconda3.6
use freesurfer
pip install --user nibabel
python makeconnseed.py --input ~/data/healthyvolunteer/mbepi_subjects_retroicorpipe_checked_aseg_fsrecon_reorient_physio.txt --output ~/data/healthyvolunteer/mbepi_subjects_retroicorpipe_checked_aseg_fsrecon_reorient_physio_connseedLRprimarymotor_Raichlenetal2016.txt --seed ~/data/atlas/LRprimarymotor_Raichlenetal2016.nii.gz --template $MNI152 --binary
