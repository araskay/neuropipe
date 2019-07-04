#!/usr/bin/env python

'''
Run fMRI preprocessing pipelines on a subjects' fMRI data.
This is the main script called by parallel processing scripts, e.g.,
ppipe.py and its variations for different HPC clusters.

To implement:
    - combined single GLM for all regressors
'''

import workflow
from pipeline import Pipeline
import fileutils
import preprocessingstep
import sys, getopt, os
import copy

def printhelp():
    print('USAGE:')
    print(('pipe.py  --subjects <subjects file>'
           ' --pipeline <pipeline file>'
           ' [--showpipe]'
           ' [--parcellate]'
           ' [--meants]'
           ' [--seedconn]'
           ' [--tomni]'
           ' [--template <template file>]'
           ' [--resout <base name>]'
           ' [--keepintermed]'
           ' [--boldregdof <dof>]'
           ' [--structregdof <dof>]'
           ' [--boldregcost <cost function>]'
           ' [--structregcost <cost function>]'
           ' [--runpipename <name>]'
           ' [--outputsubjects <subj file>]'
           ' [--showsubjects]'
           ' [--maskthresh]'
           ' [--opath <output path>]'))
    print('ARGUMENTS:')
    print('--subjects <subj file>: specify subjects file (required)')
    print('--pipeline <pipe file>: specify a pipeline file to be run on all subjects without optimization and/or calculation of between subject metrics')
    print('--showpipe: show the pipeline to be run without running. Only use to see a list of pipelines to be run/optimized. This will NOT run/optimize the pipelines. Remove the flag to run/optimize.')
    print('--parcellate: parcellate the output of the run/optimal/fixed pipeline(s).')
    print('--meants: compute mean time series over CSF, GM, and WM for the pipeline output. This automatically parcellates the output. If used with --seedconn, mean time series over the network is also computed.')
    print('--seedconn: compute seed-connectivity network on the pipeline output. Need to provide a seed file in subjects file.')
    print('--tomni: transform pipeline output and seed connectivity (if available) to standard MNI space. Requires template to be specified')
    print('--template <temp file>: template file to be used for between subject calculations, e.g., MNI template.')
    print('--keepintermed: keep results of the intermediate steps')
    print('--boldregdof <dof>: degrees of freedom to be used for bold registration (Default = 12).')
    print('--structregdof <dof>: degrees of freedom to be used for structural registration (Default = 12).')
    print('--boldregcost <cost function>: cost fuction to be used for bold registration (Default = \'corratio\').')
    print('--structregcost <cost function>: cost fuction to be used for structural registration (Default = \'corratio\').')
    print('--runpipename <name>: prefix to precede name of steps in the run pipeline output files. (Default=\'\')')
    print('--outputsubjects <subj file>: specify a subject file, to which the results of the pipeline run on all subjects is appended. Only applicable with --pipeline.')
    print('--showsubjects: print the list of all subjects to be processed and exit.')
    print('--maskthresh: threshold for binarizing functional masks transformed from structural masks (Default=0.5)')
    print('--opath <output path>: output path- overrides the opath in subjects file')
    print('Report bugs/issues to M. Aras Kayvanrad (mkayvanrad@research.baycrest.org)')


subjectsfiles=[]
runpipesteps=[] # this is a list
showpipes=False
parcellate=False
meants=False
seedconn=False
tomni=False
runpipename=''
outputsubjectsfile=''
keepintermed=False
runpipe=False
showsubjects=False
opath=''

envvars=workflow.EnvVars()

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','pipeline=', 'subjects=',
                                 'showpipe', 'parcellate', 'meants',
                                 'seedconn', 'tomni', 'template=',
                                 'boldregdof=', 'structregdof=',
                                 'boldregcost=', 'structregcost=',
                                 'outputsubjects=', 'keepintermed',
                                 'runpipename=', 'showsubjects',
                                 'maskthresh=', 'opath='])
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
    elif opt in ('--subjects'):
        subjectsfiles.append(arg)
    elif opt in ('--showpipe'):
        showpipes=True
    elif opt in ('--template'):
        envvars.mni152=arg
    elif opt in ('--parcellate'):
        parcellate=True
    elif opt in ('--meants'):
        meants=True
    elif opt in ('--seedconn'):
        seedconn=True
    elif opt in ('--tomni'):
        tomni=True
    elif opt in ('--boldregdof'):
        envvars.boldregdof=arg
    elif opt in ('--structregdof'):
        envvars.structregdof=arg
    elif opt in ('--boldregcost'):
        envvars.boldregcost=arg
    elif opt in ('--structregcost'):
        envvars.structregcost=arg
    elif opt in ('--outputsubjects'):
        outputsubjectsfile=arg
    elif opt in ('--keepintermed'):
        keepintermed=True
    elif opt in ('--runpipename'):
        runpipename=arg
    elif opt in ('--showsubjects'):
        showsubjects=True
    elif opt in ('--maskthresh'):
        envvars.maskthresh=arg
    elif opt in ('--opath'):
        opath=arg

if subjectsfiles==[]:
    sys.exit('Please specify subjects file. Get help using -h or --help.')

if tomni and envvars.mni152=='':
    sys.exit('--tomni used but template not specified. Need to provide --template to use --tomni.')

if showsubjects:
    subjects=[]
    for sfile in subjectsfiles:
        subjects+=workflow.getsubjects(sfile)
    subjcount=0
    sesscount=0
    runcount=0
    for subj in subjects:
        subjcount += 1
        for sess in subj.sessions:
            sesscount += 1
            for run in sess.runs:
                runcount += 1
                print(subj.ID, sess.ID, run.data.bold, run.data.opath)
    print('Total # subjects =',subjcount)
    print('Total # sessions =',sesscount)
    print('Total # runs =', runcount)
    sys.exit()

# run workflow
if runpipe:
    subjects=[]
    for sfile in subjectsfiles:
        subjects+=workflow.getsubjects(sfile)
    runwf=workflow.Workflow('RunWF')
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                if len(opath)>0:
                    run.data.opath=opath
                (directory,namebase)=os.path.split(run.data.bold)
                namebase=fileutils.removext(namebase)
                outpath=os.path.abspath(run.data.opath) # just to remove possible end slash (/) for consistency                
                run.data.envvars=envvars
                pipe=Pipeline(runpipename,runpipesteps)
                pipe.setibase(run.data.bold)
                pipe.setobase(outpath+'/'+namebase)
                pipe.setdata(run.data) # when running pipeline do not deepcopy so that results can be recorded if needed
                pipe.keepintermed=keepintermed
                run.addpipeline(pipe)
        runwf.addsubject(subj)
    if parcellate:
        runwf.parcellate=True
    if seedconn:
        runwf.seedconn=True
    if meants:
        runwf.meants=True
    if tomni:
        runwf.tomni=True
        
        
if showpipes:
    # print all pipelines run
    if len(runpipesteps)>0:
        print('-----')
        print('-----')
        print('Pipeline run:')
        for subj in [runwf.subjects[0]]:
            for sess in [subj.sessions[0]]:
                for run in [sess.runs[0]]:
                    for pipe in run.pipelines:
                        #print(subj.ID,'_',sess.ID,'_',run.seqname, pipe.getsteps())
                        print(run.seqname, pipe.getsteps())    

    sys.exit()
    
# now process    
if runpipe:
    runwf.run()
    if len(outputsubjectsfile)>0:
        workflow.savesubjects(outputsubjectsfile,runwf.subjects)
