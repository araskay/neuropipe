#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -M hpc3820@localhost
#$ -o /home/hpc3820/code/pipeline/output.txt
#$ -e /home/hpc3820/code/pipeline/error.txt
use anaconda3.6
use freesurfer
pip install --user nibabel
python skullstripstructural.py --input ~/data/healthyelderly/epi_subjects_checked_physio.txt --output ~/data/healthyelderly/epi_subjects_checked_physio_skullstrip.txt --keeprecon
