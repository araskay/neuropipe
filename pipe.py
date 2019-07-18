#!/usr/bin/env python

'''
Run fMRI preprocessing pipelines on a subjects' fMRI data.
This is the main script called by parallel processing scripts, e.g.,
ppipe.py and its variations for different HPC clusters.

To implement:
    - combined single GLM for all regressors
'''

import os,sys
import copy

# add pipe.py directory to path before loading other modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import workflow
from pipeline import Pipeline
import fileutils
import preprocessingstep

import parse

parser = parse.ParseArgs(sys.argv[1:])

if parser.showsubjects:
    subjects=[]
    for sfile in parser.subjectsfiles:
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
if parser.runpipe:
    subjects=[]
    for sfile in parser.subjectsfiles:
        subjects+=workflow.getsubjects(sfile)
    runwf=workflow.Workflow('RunWF')
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                if len(parser.opath)>0:
                    run.data.opath=parser.opath
                (directory,namebase)=os.path.split(run.data.bold)
                namebase=fileutils.removext(namebase)
                outpath=os.path.abspath(run.data.opath) # just to remove possible end slash (/) for consistency                
                run.data.envvars=parser.envvars
                pipe=Pipeline(parser.runpipename,parser.runpipesteps)
                pipe.setibase(run.data.bold)
                pipe.setobase(outpath+'/'+namebase)
                pipe.setdata(run.data) # when running pipeline do not deepcopy so that results can be recorded if needed
                pipe.keepintermed=parser.keepintermed
                run.addpipeline(pipe)
        runwf.addsubject(subj)
    if parser.parcellate:
        runwf.parcellate=True
    if parser.seedconn:
        runwf.seedconn=True
    if parser.meants:
        runwf.meants=True
    if parser.tomni:
        runwf.tomni=True
        
        
if parser.showpipes:
    # print all pipelines run
    if len(parser.runpipesteps)>0:
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
if parser.runpipe:
    runwf.run()
    if len(parser.outputsubjectsfile)>0:
        workflow.savesubjects(parser.outputsubjectsfile,runwf.subjects)
