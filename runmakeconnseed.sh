#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -M hpc3820@localhost
#$ -o /home/hpc3820/code/pipeline/runmakeconnseed_output.txt
#$ -e /home/hpc3820/code/pipeline/runmakeconnseed_error.txt
use anaconda3.6
use freesurfer
pip install --user nibabel
python makeconnseed.py --input ~/data/healthyvolunteer/fepi_subjects_checked_physio_skullstrip_reorient_connseedcordinates_aseg__corratio_registrations.txt --output ~/data/healthyvolunteer/fepi_subjects_checked_physio_skullstrip_reorient_connseedcordinates_aseg__corratio_registrations_connseed.txt --seed ~/data/atlas/LRprimarymotor_Raichlenetal2016.nii.gz --template $MNI152 --binary --boldregdof 6
