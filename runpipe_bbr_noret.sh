#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -M hpc3820@localhost
#$ -o /home/hpc3820/code/pipeline/runpipe_bbr_noret_output.txt
#$ -e /home/hpc3820/code/pipeline/runpipe_bbr_noret_error.txt
use anaconda3.6
use freesurfer
pip install --user nibabel
python pipe.py --subject ~/data/healthyvolunteer/fepi_subjects_checked_physio_skullstrip_reorient_connseedcordinates_aseg__bbr.txt --pipeline ~/data/healthyvolunteer/processed/pipeline_noRet.txt --template $MNI152 --meants --seedconn --boldregdof 6 --boldregcost bbr
