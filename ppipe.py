#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  3 13:48:29 2018

@author: aras
"""

#!/usr/bin/env python

def printhelp():
    print('USAGE:')
    print('pipe.py  --subjects <subjects file> --pipeline <pipeline file> --perm <pipeline file> --onoff <pipeline file> --const <pipeline file> --add --combine --fixed <pipeline file> --showpipes --template <template file> --resout <base name>')
    print('ARGUMENTS:')
    print('--subjects <subj file>: specify subjects file (required)')
    print('--pipeline <pipe file>: specify a pipeline file to be run on all subjects without optimization and/or calculation of between subject metrics')
    print('--const <pipe file>: specify a pipeline file to be used to form constant section of the optimized pipeline')
    print('--perm <pipe file>: specify a pipeline file to be used to form permutations section of the optimized pipeline')
    print('--onoff <pipe file>: specify a pipeline file to be used to form on/off section of the optimized pipeline')
    print('--permonoff <pipe file>: on/off combinations and their permutations')
    print('--select <pipe file>: select one step from the pipe file at a time')
    print('--combine: flag specifying that all new (permutation/on-off/constant) steps are combined with the previous ones from this point on (Default) (See example below)')
    print('--add: flag specifying that all new (permutation/on-off/constant) steps are added to the previous pipelines from this point on (Default is combine) (See example below)')
    print('--fixed <pipe file>: specify a fixed pipeline for the calculation of between subject metrics')
    print('--showpipes: show all pipelines to be run/optimized/validated without running. Only use to see a list of pipelines to be run/optimized. This will NOT run/optimize the pipelines. Remove the flag to run/optimize.')
    print('--template <temp file>: template file to be used for between subject calculations, e.g., MNI template. Required with --perm, --onoff, --const, --fixed, unless using --showpipes.')
    print('--resout <base name>: base path/name to save results in csv format. Extension (.csv) and suffixed are added to the base name.')
    print('--parcellate: parcellate the output of the run/optimal/fixed pipeline(s).')
    print('--meants: compute mean time series over CSF, GM, and WM for the pipeline output. This automatically parcellates the output. If used with --seedconn, mean time series over the network is also computed.')
    print('--seedconn: compute seed-connectivity network on the pipeline output. Need to provide a seed file in subjects file.')
    print('--tomni: transform pipeline output and seed connectivity (if used --seedconn) to standard MNI space.')
    print('--keepintermed: keep results of the intermediate steps')
    print('--boldregdof <dof>: degrees of freedom to be used for bold registration (Default = 12).')
    print('--structregdof <dof>: degrees of freedom to be used for structural registration (Default = 12).')
    print('--boldregcost <cost function>: cost fuction to be used for bold registration (Default = \'corratio\').')
    print('--structregcost <cost function>: cost fuction to be used for structural registration (Default = \'corratio\').')
    print('--runpipename <name>: prefix to precede name of steps in the run pipeline output files. (Default=\'\')')
    print('--fixpipename <name>: prefix to precede name of steps in the fixed pipeline output files. (Default=\'fix\')')
    print('--optpipename <name>: prefix to precede name of steps in the optimal pipeline output files. (Default=\'opt\')')
    print('--outputsubjects <subj file>: specify a subject file, which is populated based on the results of the pipeline run on all subjects. Only applicable with --pipeline.')
    print('Report bugs/issues to M. Aras Kayvanrad (mkayvanrad@research.baycrest.org)')

import workflow
from pipeline import Pipeline
from preprocessingstep import PreprocessingStep
import fileutils
import preprocessingstep
import sys, getopt, os
import copy

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

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','pipeline=', 'subjects=', 'perm=', 'onoff=', 'permonoff=', 'const=', 'select=', 'add', 'combine', 'fixed=', 'showpipes', 'template=', 'resout=', 'parcellate', 'meants', 'seedconn', 'tomni', 'boldregdof=', 'structregdof=', 'boldregcost=', 'structregcost=', 'outputsubjects=', 'keepintermed', 'runpipename=', 'fixpipename=', 'optpipename='])
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

if subjectsfiles==[]:
    print('Please specify subjects file. Get help using -h or --help.')

if runpipe:
    subjects=[]
    count=0
    qbatch_fname = 'qbatch_jobs.job'
    qbatch_file = open(qbatch_fname, 'w')
    base_command = 'python pipe.py'

    for sfile in subjectsfiles:
        subjects=workflow.getsubjects(sfile)

        for s in subjects:
            count+=1
            subject_fname = '__temp_subj_file_'+str(count)+'.txt'
            workflow.savesubjects(subject_fname,[s])
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
            command_str  = ' '.join(pipe_args)
            qbatch_file.write(command_str)
            qbatch_file.write('\n')


    qbatch_file.close()
