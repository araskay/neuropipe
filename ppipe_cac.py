#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os
import subprocess

# add pipe.py directory to path before loading other modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
        qbatch_file.write('#SBATCH -t 48:0:0\n')
        qbatch_file.write('#SBATCH -o .temp_job_'+parser.subjfile+'_'+parser.pipefile+str(count)+'.o'+'\n')
        qbatch_file.write('#SBATCH -e .temp_job_'+parser.subjfile+'_'+parser.pipefile+str(count)+'.e'+'\n\n')

        qbatch_file.write('module load anaconda/3.5.3\n')
        qbatch_file.write('module load afni\n')
        qbatch_file.write('module load fsl\n')
        qbatch_file.write('module load freesurfer\n')
        qbatch_file.write('module load matlab\n')
        qbatch_file.write('module load anaconda/3.5.3\n\n')
                              
        command_str  = ' '.join(parser.replace_subjectsfile(subject_fname))
        qbatch_file.write(command_str)
        qbatch_file.write('\n')
        
        qbatch_file.close()
        
        # now submit job
        p=subprocess.Popen(['sbatch',qbatch_fname])
        p.communicate()            

print('Total of '+str(count)+' jobs submitted.')
