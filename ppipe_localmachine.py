#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  3 13:48:29 2018

@author: aras
"""

def printhelp():
    p=subprocess.Popen(['pipe.py','-h'])
    p.communicate()
    print('---------------------------------------')
    print('Additional parallel processing options:')
    print('[--numpar <number of parallel jobs = 16>]')

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

numpar=16

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
                       '--optpipename','--numpar']:
            printhelp()
            sys.exit()


runpipefile=''
subjfile=''

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','pipeline=', 'subjects=', 'perm=', 'onoff=', 'permonoff=', 'const=', 'select=', 'add', 'combine', 'fixed=', 'showpipes', 'template=', 'resout=', 'parcellate', 'meants', 'seedconn', 'tomni', 'boldregdof=', 'structregdof=', 'boldregcost=', 'structregcost=', 'outputsubjects=', 'keepintermed', 'runpipename=', 'fixpipename=', 'optpipename=','numpar='])
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
    elif opt in ('--numpar'):
        numpar=int(arg)

if subjectsfiles==[]:
    sys.exit('Please specify subjects file. Get help using -h or --help.')

base_command = 'pipe.py'

if runpipe:

    subjects=[]

    count=0
    proccount=0
    processes = []

    for sfile in subjectsfiles:
        subjects=workflow.getsubjects(sfile)

        for s in subjects:
            # first create individual subjects files and job bash scripts to be
            # submitted to the job manager
            count+=1
            proccount+=1

            subject_fname = '.temp_subj_'+subjfile+'_'+runpipefile+str(count)+'.txt'
            
            command=[]
       
            workflow.savesubjects(subject_fname,[s],append=False)
            
            # write the header stuff
            outputfile='.temp_job_'+subjfile+'_'+runpipefile+str(count)+'.o'
            errorfile='.temp_job_'+subjfile+'_'+runpipefile+str(count)+'.e'

            f_o = open(outputfile, 'w')
            f_e = open(errorfile, 'w')
        
            command.append(base_command)
            #Just re-use the arguments given here
            pipe_args = sys.argv[1:]

            pipe_args[pipe_args.index('--subjects')+1] = subject_fname

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

