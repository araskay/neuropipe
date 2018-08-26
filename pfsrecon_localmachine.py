#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys,getopt,subprocess,os
import workflow

def printhelp():
    p=subprocess.Popen(['fsrecon.py','-h'])
    p.communicate()
    print('---------------------------------')
    print('Additional job scheduler options:')
    print('[--numpar <number of parallel jobs = 16>]')

ifile=''
ofile=''

# the getopt libraray somehow "guesses" the arguments- for example if given
# '--subject' it will automatically produce '--subjects'. This can cause problems
# later when arguments from sys.argv are passed to pipe.py. The following checks
# in advance to avoid such problems
pipe_args = sys.argv[1:]
for arg in pipe_args:
    if '--' in arg:
        if not arg in ['--help','--input', '--output', '--directive','--numpar']:
            printhelp()
            sys.exit()

numpar=16

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:',['help','input=', 'output=', 'directive=','numpar='])
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

    elif opt in ('--numpar'):
        numpar=int(arg)

if ifile=='' or ofile=='':
    printhelp()
    sys.exit()

base_command = 'fsrecon.py'

count=0
proccount=0
processes = []

subjects=workflow.getsubjects(ifile)

# get input file name to use for naming temporary files
(directory,filename)=os.path.split(ifile)

for s in subjects:
    # first create individual subjects files and job bash scripts to be
    # submitted to the job manager
    count+=1
    proccount+=1

    subject_fname = '.temp_fsrecon_subj_'+filename+str(count)+'.txt'

    command=[]

    workflow.savesubjects(subject_fname,[s],append=False)

    outputfile='.temp_fsrecon_job_'+filename+str(count)+'.o'
    errorfile='.temp_fsrecon_job_'+filename+str(count)+'.e'

    f_o = open(outputfile, 'w')
    f_e = open(errorfile, 'w')

    command.append(base_command)
    #Just re-use the arguments given here
    pipe_args = sys.argv[1:]

    pipe_args[pipe_args.index('--input')+1] = subject_fname

    if '--numpar' in pipe_args:
        del pipe_args[pipe_args.index('--numpar')+1]
        del pipe_args[pipe_args.index('--numpar')]

    command = command+ pipe_args
    
    # now submit job
    print('Running',' '.join(command))
    p=subprocess.Popen(command,stdout=f_o,stderr=f_e)
    processes.append(p)

    if proccount==numpar:
        for p in processes:
            p.wait()
        proccount=0
        processes=[]
        print('Total of',count,'jobs done')

for p in processes:
    p.wait()           


