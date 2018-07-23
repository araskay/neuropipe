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
import preprocessingstep
import sys, getopt, os
import subprocess

subjectsfiles=[]
combs=[]
addsteps=False
runpipesteps=[] # this is a list
optimalpipesteps=[] # this is a list of lists
fixedpipesteps=[] # this is a list
showpipes=False
resout=''
parcellate=False
meants=False
seedconn=False
tomni=False
runpipename=''
optpipename='opt'
fixpipename='fix'
outputsubjectsfile=''
keepintermed=False
runpipe=False

envvars=workflow.EnvVars()

# the getopt libraray somehow "guesses" the arguments- for example if given
# '--subject' it will automatically produce '--subjects'. This can cause problems
# later when arguments from sys.argv are passed to pipe.py. The following checks
# in advance to avoid such problems
pipe_args = sys.argv[1:]
for arg in pipe_args:
    if '--' in arg:
        if not arg in ['--help','--pipeline', '--subjects', '--perm', '--onoff',\
                       '--permonoff', '--const', '--select', '--add',\
                       '--combine', '--fixed', '--showpipes', '--template',\
                       '--resout', '--parcellate', '--meants', '--seedconn',\
                       '--tomni', '--boldregdof', '--structregdof',\
                       '--boldregcost', '--structregcost', '--outputsubjects',\
                       '--keepintermed', '--runpipename', '--fixpipename',\
                       '--optpipename']:
            printhelp()
            sys.exit()


runpipefile=''
subjfile=''
mem='16'

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','pipeline=', 'subjects=', 'perm=', 'onoff=', 'permonoff=', 'const=', 'select=', 'add', 'combine', 'fixed=', 'showpipes', 'template=', 'resout=', 'parcellate', 'meants', 'seedconn', 'tomni', 'boldregdof=', 'structregdof=', 'boldregcost=', 'structregcost=', 'outputsubjects=', 'keepintermed', 'runpipename=', 'fixpipename=', 'optpipename=','mem='])
except getopt.GetoptError:
    printhelp()
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        printhelp()
        sys.exit()
    elif opt in ('--pipeline'):
        runpipesteps+=preprocessingstep.makesteps(arg)
        runpipe=True
        (directory,runpipefile)=os.path.split(arg)
        #(directory,namebase)=os.path.split(arg)
        #namebase=fileutils.removext(namebase)
        #runpipename+=namebase
    elif opt in ('--fixed'):
        fixedpipesteps+=preprocessingstep.makesteps(arg)
    elif opt in ('--perm'):
        steps=preprocessingstep.makesteps(arg)
        if addsteps:
            optimalpipesteps+=list(preprocessingstep.permutations(steps))
        else:
            optimalpipesteps=list(preprocessingstep.concatstepslists(optimalpipesteps,\
                                                                     list(preprocessingstep.permutations(steps))))
    elif opt in ('--onoff'):
        steps=preprocessingstep.makesteps(arg)
        if addsteps:
            optimalpipesteps+=list(preprocessingstep.onoff(steps))
        else:
            optimalpipesteps=list(preprocessingstep.concatstepslists(optimalpipesteps,\
                                                                     list(preprocessingstep.onoff(steps))))

    elif opt in ('--permonoff'):
        steps=preprocessingstep.makesteps(arg)
        if addsteps:
            optimalpipesteps+=list(preprocessingstep.permonoff(steps))
        else:
            optimalpipesteps=list(preprocessingstep.concatstepslists(optimalpipesteps,\
                                                                     list(preprocessingstep.permonoff(steps))))

    elif opt in ('--select'):
        steps=preprocessingstep.makesteps(arg)
        if addsteps:
            optimalpipesteps+=list(preprocessingstep.select(steps))
        else:
            optimalpipesteps=list(preprocessingstep.concatstepslists(optimalpipesteps,\
                                                                     list(preprocessingstep.select(steps))))

    elif opt in ('--const'):
        steps=preprocessingstep.makesteps(arg)
        if addsteps:
            optimalpipesteps+=[steps]
        else:
            optimalpipesteps=list(preprocessingstep.concatstepslists(optimalpipesteps,[steps]))
    elif opt in ('--subjects'):
        subjectsfiles.append(arg)
        (directory,subjfile)=os.path.split(arg) # this is inconsistent with the idea of having multiple subject files- maybe just get one subjects file?
    elif opt in ('--mem'):
        mem=arg

if subjectsfiles==[]:
    print('Please specify subjects file. Get help using -h or --help.')


base_command = 'pipe.py'

if runpipe:

    subjects=[]
    count=0

    for sfile in subjectsfiles:
        subjects=workflow.getsubjects(sfile)

        for s in subjects:
            # first create individual subjects files and job bash scripts to be
            # submitted to the job manager
            count+=1
            subject_fname = '.temp_subj_'+subjfile+'_'+runpipefile+str(count)+'.txt'
            qbatch_fname = '.temp_job_'+subjfile+'_'+runpipefile+str(count)+'.sh'
            qbatch_file = open(qbatch_fname, 'w')
            
            workflow.savesubjects(subject_fname,[s],append=False)
            
            # write the header stuff
            qbatch_file.write('#!/bin/bash\n\n')
            qbatch_file.write('#SBATCH -c 1\n')
            qbatch_file.write('#SBATCH --mem='+mem+'g\n')
            qbatch_file.write('#SBATCH -t 48:0:0\n')
            qbatch_file.write('#SBATCH -o .temp_job_'+subjfile+'_'+runpipefile+str(count)+'.o'+'\n')
            qbatch_file.write('#SBATCH -e .temp_job_'+subjfile+'_'+runpipefile+str(count)+'.e'+'\n\n')

            qbatch_file.write('module load anaconda/3.5.3\n')
            qbatch_file.write('module load afni\n')
            qbatch_file.write('module load fsl\n')
            qbatch_file.write('module load freesurfer\n')
            qbatch_file.write('module load anaconda/3.5.3\n\n')
                              
            qbatch_file.write(base_command + ' ')
            #Just re-use the arguments given here
            pipe_args = sys.argv[1:]
#            indx = 0
            #When we make the commands for each process, we need to swap out the
            #argument for --subjects with our new subject lists
            #We make the (hopefully valid) assumption that the piece directly
            #after the --subjects argument is what we need to replace
#            while(indx < len(pipe_args)):
#                if(pipe_args[indx] == '--subjects'):
#                        pipe_args[indx + 1] = subject_fname
#                indx += 1
            pipe_args[pipe_args.index('--subjects')+1] = subject_fname
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

