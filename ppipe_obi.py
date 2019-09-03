#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Thisis a wrapper to run parallel pipe.py jobs on HPC clusters.
Input arguments are the same as pipe.py with the additional argument --mem
to set the memory requtest per node.
The input subjects file is split into individual subjects, each of which is run
separately on a separate core.
This script is base don the SLURM job scheduler on the Queen's Universriy CAC
cluster, but can be modify to suit other job schedulers.
Report bugs/issues to Aras Kayvanrad (mkayvan@gmail.com).
# (c) Aras Kayvanrad
"""

import sys, os
import subprocess

import distutils.spawn

# check if pipe.py is accessible and if yes,
# add pipe.py directory to path before loading other modules
if distutils.spawn.find_executable('pipe.py') == None:
    print('Cannot find pipe.py. Possible causes/solutions:')
    print('- Make sure the installation directory is added to the path')
    print('- Alternatively you can run directly from the installation directory.')
    sys.exit()
sys.path.insert(0,distutils.spawn.find_executable('pipe.py'))

import workflow
import parse

parser = parse.ParseArgs(sys.argv[1:], mem=16)

base_command = 'pipe.py'

subjects=[]
count=0

for sfile in parser.subjectsfiles:
    subjects=workflow.getsubjects(sfile)

    for s in subjects:
        # first create individual subjects files and job bash scripts to be
        # submitted to the job manager
        count+=1
        subject_fname = '.temp_subj_'+parser.subjfile+'_'+parser.pipefile+str(count)+'.txt'
        qbatch_fname = '.temp_job_'+parser.subjfile+'_'+parser.pipefile+str(count)+'.sh'
        qbatch_file = open(qbatch_fname, 'w')
        
        workflow.savesubjects(subject_fname,[s],append=False)
        
        # write the header stuff
        qbatch_file.write('#!/bin/bash\n\n')
        qbatch_file.write('#SBATCH -c 1\n')
        qbatch_file.write('#SBATCH --mem='+str(parser.mem)+'g\n')
        qbatch_file.write('#SBATCH -t 240:0:0\n')
        qbatch_file.write('#SBATCH -o .temp_job_'+parser.subjfile+'_'+parser.pipefile+str(count)+'.o'+'\n')
        qbatch_file.write('#SBATCH -e .temp_job_'+parser.subjfile+'_'+parser.pipefile+str(count)+'.e'+'\n\n')

        qbatch_file.write('#SBATCH --partition=reserved\n')
        qbatch_file.write('#SBATCH --account=rac-2018-hpcg1699\n\n')

        qbatch_file.write('module load anaconda/3.5.3\n')
        qbatch_file.write('module load afni\n')
        qbatch_file.write('module load fsl\n')
        qbatch_file.write('module load freesurfer\n')
        qbatch_file.write('module load matlab\n')
        qbatch_file.write('module load anaconda/3.5.3\n\n')
                          
        qbatch_file.write(base_command + ' ')

        command_str  = ' '.join(parser.replace_subjectsfile(subject_fname))
        qbatch_file.write(command_str)
        qbatch_file.write('\n')
        
        qbatch_file.close()
        
        # now submit job
        p=subprocess.Popen(['sbatch',qbatch_fname])
        p.communicate()            

print('Total of '+str(count)+' jobs submitted.')
