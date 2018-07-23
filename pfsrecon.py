#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys,getopt,subprocess,os
import workflow

def printhelp():
    p=subprocess.Popen(['fsrecon.py','-h'])
    p.communicate()
    print('---------------------------------')
    print('Additional job scheduler options:')
    print('--mem <amount in GB = 16>')

ifile=''
ofile=''

# the getopt libraray somehow "guesses" the arguments- for example if given
# '--subject' it will automatically produce '--subjects'. This can cause problems
# later when arguments from sys.argv are passed to pipe.py. The following checks
# in advance to avoid such problems
pipe_args = sys.argv[1:]
for arg in pipe_args:
    if '--' in arg:
        if not arg in ['--help','--input', '--output', '--directive','--mem']:
            printhelp()
            sys.exit()

mem='16'

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:',['help','input=', 'output=', 'directive=','mem='])
except getopt.GetoptError:
    printhelp()
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        printhelp()
        sys.exit()
    elif opt in ('--input'):
        ifile=arg
    elif opt in ('--output'):
        ofile=arg        

    elif opt in ('--mem'):
        mem=arg

if ifile=='' or ofile=='':
    printhelp()
    sys.exit()

base_command = 'fsrecon.py'

count=0

subjects=workflow.getsubjects(ifile)

# get input file name to use for naming temporary files
(directory,filename)=os.path.split(ifile)

for s in subjects:
    # first create individual subjects files and job bash scripts to be
    # submitted to the job manager
    count+=1
    subject_fname = '.temp_fsrecon_subj_'+filename+str(count)+'.txt'
    qbatch_fname = '.temp_fsrecon_job_'+filename+str(count)+'.sh'
    qbatch_file = open(qbatch_fname, 'w')
    
    workflow.savesubjects(subject_fname,[s],append=False)

    # write the header stuff
    qbatch_file.write('#!/bin/bash\n\n')
    qbatch_file.write('#SBATCH -c 1\n')
    qbatch_file.write('#SBATCH --mem='+mem+'g\n')
    qbatch_file.write('#SBATCH -t 72:0:0\n')
    qbatch_file.write('#SBATCH -o .temp_fsrecon_job_'+filename+str(count)+'.o'+'\n')
    qbatch_file.write('#SBATCH -e .temp_fsrecon_job_'+filename+str(count)+'.e'+'\n\n')

    qbatch_file.write('module load anaconda/3.5.3\n')
    #qbatch_file.write('module load afni\n')
    #qbatch_file.write('module load fsl\n')
    qbatch_file.write('module load freesurfer\n')
    qbatch_file.write('module load anaconda/3.5.3\n\n')
                      
    qbatch_file.write(base_command + ' ')
    #Just re-use the arguments given here
    pipe_args = sys.argv[1:]
    pipe_args[pipe_args.index('--input')+1] = subject_fname
    if '--mem' in pipe_args:
        del pipe_args[pipe_args.index('--mem')+1]
        del pipe_args[pipe_args.index('--mem')]
    command_str  = ' '.join(pipe_args)
    qbatch_file.write(command_str)
    qbatch_file.write('\n')
    
    qbatch_file.close()
    
    # now submit job
    p=subprocess.Popen(['sbatch',qbatch_fname])
    p.communicate()            

