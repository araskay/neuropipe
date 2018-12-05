#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  3 13:48:29 2018

@author: aras
"""

# Use this script to run parallel pipe.py jobs on a machine with multiple cores.
# Input arguments are the same as pipe.py with the additional argument --numpar
# to set the maximum number of parallel jobs to be run simultaneously.
# The input subjects file is split into individual subjects, each of which is run separately on a core.
# Report bugs/issues to M. Aras Kayvanrad (mkayvan@gmail.com).
# (c) M. Aras Kayvanrad

def printhelp():
    p=subprocess.Popen(['pipe.py','-h'])
    p.communicate()
    print('---------------------------------------')
    print('Additional parallel processing options:')
    print('[--numpar <number of parallel jobs = 16>]')

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
proccount=0
processes = []

for sfile in args.subjectsfiles:
    subjects=workflow.getsubjects(sfile)

    for s in subjects:
        # first create individual subjects files and job bash scripts to be
        # submitted to the job manager
        count+=1
        proccount+=1

        subject_fname = '.temp_subj_'+args.subjfile+'_'+args.pipefile+str(count)+'.txt'
        
        command=[]
   
        workflow.savesubjects(subject_fname,[s],append=False)
        
        # write the header stuff
        outputfile='.temp_job_'+args.subjfile+'_'+args.pipefile+str(count)+'.o'
        errorfile='.temp_job_'+args.subjfile+'_'+args.pipefile+str(count)+'.e'

        f_o = open(outputfile, 'w')
        f_e = open(errorfile, 'w')
    
        command.append(base_command)

        command = command + ppipe_utils.getjobargs(pipe_args, subject_fname)
        
        # now submit job
        print('Running',' '.join(command))
        p=subprocess.Popen(command,stdout=f_o,stderr=f_e)
        processes.append(p)

        if proccount==args.numpar:
            for p in processes:
                p.wait()
            proccount=0
            processes=[]
            print('Total of',count,'jobs done')

for p in processes:
    p.wait()            

