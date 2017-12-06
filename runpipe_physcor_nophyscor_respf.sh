#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -M hpc3820@localhost
#$ -o /home/hpc3820/code/pipeline/runpipe_physcor_nophyscor_respf_output.txt
#$ -e /home/hpc3820/code/pipeline/runpipe_physcor_nophyscor_respf_error.txt
use anaconda3.6
use freesurfer
pip install --user nibabel
pip install --user nipype
python pipe.py --subjects ~/data/healthyvolunteer/fepi_subjects_physcor_checked_physio_skullstrip_reorient_connseedcordinates_aseg_registrations_connseed.txt --fixed ~/data/healthyvolunteer/processed/pipe_physcor_const.txt --fixed ~/data/healthyvolunteer/processed/pipe_physcor_respfreq.txt --template $MNI152 --meants --seedconn --resout /u1/work/hpc3820/data/healthyvolunteer/processed/physcor/pipe_physcor_nophyscor_respf --fixpipename nophyscor_respf --keepintermed

