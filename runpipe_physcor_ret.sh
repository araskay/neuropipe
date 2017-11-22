#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -M hpc3820@localhost
#$ -o /home/hpc3820/code/pipeline/runpipe_physcor_ret_output.txt
#$ -e /home/hpc3820/code/pipeline/runpipe_physcor_ret_error.txt
use anaconda3.6
use freesurfer
pip install --user nibabel
pip install --user nipype
python pipe.py --subjects ~/data/healthyvolunteer/fepi_subjects_physcor_checked_physio_skullstrip_reorient_connseedcordinates_aseg_registrations_connseed.txt --fixed ~/data/healthyvolunteer/processed/pipe_physcor_const.txt --fixed ~/data/healthyvolunteer/processed/pipe_physcor_ret.txt --template $MNI152 --meants --seedconn --resout ~/data/healthyvolunteer/processed/pipe_physcor_ret --fixpipename ret

