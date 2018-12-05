#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  3 13:48:29 2018

@author: aras
"""

def printhelp():
    p=subprocess.Popen(['pipe.py','-h'])
    p.communicate()
    print('---------------------------------')
    print('Additional job scheduler options:')
    print('--mem <amount in GB = 16>')

import workflow
import sys
import subprocess
import ppipe_utils

# the getopt libraray somehow "guesses" the arguments- for example if given
# '--subject' it will automatically produce '--subjects'. This can cause problems
# later when arguments from sys.argv are passed to pipe.py. The following checks
# in advance to avoid such problems
pipe_args = sys.argv[1:]
if not ppipe_utils.argsvalid(pipe_args):
    printhelp()
    sys.exit()

args=ppipe_utils.parseargs(pipe_args)

if args.help or args.error:
    printhelp()
    sys.exit()

if args.subjectsfiles==[]:
    print('Please specify subjects file. Get help using -h or --help.')
    sys.exit()

base_command = 'pipe.py'

subjects=[]
count=0

for sfile in args.subjectsfiles:
    subjects=workflow.getsubjects(sfile)

    for s in subjects:
        # first create individual subjects files and job bash scripts to be
        # submitted to the job manager
        count+=1
        subject_fname = '.temp_subj_'+args.subjfile+'_'+args.pipefile+str(count)+'.txt'
        qbatch_fname = '.temp_job_'+args.subjfile+'_'+args.pipefile+str(count)+'.sh'
        qbatch_file = open(qbatch_fname, 'w')
        
        workflow.savesubjects(subject_fname,[s],append=False)
        
        # write the header stuff
        qbatch_file.write('#!/bin/bash\n\n')
        qbatch_file.write('#SBATCH -c 1\n')
        qbatch_file.write('#SBATCH --mem='+args.mem+'g\n')
        qbatch_file.write('#SBATCH -t 240:0:0\n')
        qbatch_file.write('#SBATCH -o .temp_job_'+args.subjfile+'_'+args.pipefile+str(count)+'.o'+'\n')
        qbatch_file.write('#SBATCH -e .temp_job_'+args.subjfile+'_'+args.pipefile+str(count)+'.e'+'\n\n')

        qbatch_file.write('#SBATCH --partition=reserved\n')
        qbatch_file.write('#SBATCH --account=rac-2018-hpcg1699\n\n')

        qbatch_file.write('module load anaconda/3.5.3\n')
        qbatch_file.write('module load afni\n')
        qbatch_file.write('module load fsl\n')
        qbatch_file.write('module load freesurfer\n')
        qbatch_file.write('module load matlab\n')
        qbatch_file.write('module load anaconda/3.5.3\n\n')
                          
        qbatch_file.write(base_command + ' ')

        command_str  = ' '.join(ppipe_utils.getjobargs(pipe_args, subject_fname))
        qbatch_file.write(command_str)
        qbatch_file.write('\n')
        
        qbatch_file.close()
        
        # now submit job
        p=subprocess.Popen(['sbatch',qbatch_fname])
        p.communicate()            

print('Total of '+str(count)+' jobs submitted.')
