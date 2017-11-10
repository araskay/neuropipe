#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -M hpc3820@localhost
#$ -o /home/hpc3820/code/pipeline/runpipe_opt_output.txt
#$ -e /home/hpc3820/code/pipeline/runpipe_opt_error.txt
use anaconda3.6
use freesurfer
pip install --user nibabel
python pipe.py --subject ~/data/healthyvolunteer/fepi_subjects_checked_physio_skullstrip_reorient_connseedcordinates_aseg_registrations_connseed.txt --perm ~/data/healthyvolunteer/processed/scmc.txt --const ~/data/healthyvolunteer/processed/be.txt --perm ~/data/healthyvolunteer/processed/ssmooth_hpf_ret.txt --template $MNI152 --meants --seedconn --tomni --boldregdof 6
