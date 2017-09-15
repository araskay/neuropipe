import workflow
from pipeline import Pipeline
from preprocessingstep import PreprocessingStep
import fileutils
import preprocessingstep
import sys, getopt, os
import copy

subjectsfiles=[]
combs=[]
addsteps=True
runpipesteps=[] # this is a list
optimalpipesteps=[] # this is a list of lists
fixedpipesteps=[] # this is a list
showpipes=False

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hp:s:',\
                                ['help','pipeline=', 'subjects=', 'perm=', 'onoff=', 'const=', 'add', 'combine', 'fixed=', 'showpipes'])
except getopt.GetoptError:
    print('usage: testbench_workflow.py -p <pipeline text file> -s <subjects file>')
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        print('usage: testbench_workflow.py -p <pipeline text file> -s <subjects file>')
        sys.exit()
    elif opt in ('-p','--pipeline'):
        runpipesteps+=preprocessingstep.makesteps(arg)
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
    elif opt in ('--const'):
        steps=preprocessingstep.makesteps(arg)
        if addsteps:
            optimalpipesteps+=[steps]
        else:
            optimalpipesteps=list(preprocessingstep.concatstepslists(optimalpipesteps,[steps]))
    elif opt in ('-s','--subjects'):
        subjectsfiles.append(arg)
    elif opt in ('--add'):
        addsteps=True
    elif opt in ('--combine'):
        addsteps=False
    elif opt in ('--showpipes'):
        showpipes=True
        
# run workflow
if len(runpipesteps)>0:
    runwf=workflow.Workflow('Run Pipe')
    subjects=[]
    for sfile in subjectsfiles:
        subjects=subjects+workflow.getsubjects(sfile)
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                pipe=Pipeline('runpipe',runpipesteps)
                pipe.setibase(run.data.bold)
                pipe.setobase(run.data.opath)
                pipe.setdata(run.data) # when running pipeline do not deepcopy so that results, e.g., motpar, can be recorded
                #pipe.setconnectivityseedfile(run.data.connseed)
                run.addpipeline(pipe)
        runwf.addsubject(subj)

# optimal workflow
if len(optimalpipesteps)>0:
    optimalwf=workflow.Workflow('Optimal Pipe')
    subjects=[]
    for sfile in subjectsfiles:
        subjects=subjects+workflow.getsubjects(sfile)
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                count=0
                for steps in optimalpipesteps:
                    count=count+1
                    pipe=Pipeline('pipe'+str(count),steps)
                    pipe.setibase(run.data.bold)
                    pipe.setobase(run.data.opath)
                    pipe.setdata(copy.deepcopy(run.data))
                    #pipe.setconnectivityseedfile(run.data.connseed)
                    run.addpipeline(pipe)
        optimalwf.addsubject(subj)
# fixed workflow
if len(fixedpipesteps)>0:
    fixedwf=workflow.Workflow('Fixed Pipe')
    subjects=[]
    for sfile in subjectsfiles:
        subjects=subjects+workflow.getsubjects(sfile)
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                pipe=Pipeline('fixedpipe',fixedpipesteps)
                pipe.setibase(run.data.bold)
                pipe.setobase(run.data.opath)
                pipe.setdata(copy.deepcopy(run.data))
                #pipe.setconnectivityseedfile(run.data.connseed)
                run.addpipeline(pipe)
        fixedwf.addsubject(subj)

# now process
if not showpipes:
    if len(runpipesteps)>0:
        runwf.process()

    if len(optimalpipesteps)>0:
        seqname=optimalwf.subjects[0].sessions[0].runs[0].seqname # pick the 1st subject's 1st session's 1st run's sequnce
        optimalwf.computebetweensubjectreproducibility(seqname)
    if len(fixedpipesteps)>0:
        seqname=fixedwf.subjects[0].sessions[0].runs[0].seqname # pick the 1st subject's 1st session's 1st run's sequnce
        fixedwf.computebetweensubjectreproducibility(seqname)

# print all pipelines run
if len(runpipesteps)>0:
    print('-----')
    print('-----')
    print('Runned pipelines:')
    for subj in [runwf.subjects[0]]:
        for sess in [subj.sessions[0]]:
            for run in [sess.runs[0]]:
                for pipe in run.pipelines:
                    #print(subj.ID,'_',sess.ID,'_',run.seqname, pipe.getsteps())
                    print(run.seqname, pipe.getsteps())
if len(fixedpipesteps)>0:
    print('-----')
    print('-----')    
    print('Fixed pipelines:')
    for subj in [fixedwf.subjects[0]]:
        for sess in [subj.sessions[0]]:
            for run in [sess.runs[0]]:
                for pipe in run.pipelines:
                    #print(subj.ID,'_',sess.ID,'_',run.seqname, pipe.getsteps())
                    print(run.seqname, pipe.getsteps())
    print('-----')
    for betsubj in fixedwf.betweensubjectreproducibility:
        print(betsubj.subject1.ID,'_',betsubj.session1.ID, \
              'Optimal pipeline:',betsubj.run1.optimalpipeline.getsteps(), \
              'S-H Reproducibility:',betsubj.run1.optimalpipeline.splithalfseedconnreproducibility)
        print(betsubj.subject2.ID,'_',betsubj.session2.ID, \
              'Optimal pipeline:',betsubj.run2.optimalpipeline.getsteps(), \
              'S-H Reproducibility:',betsubj.run2.optimalpipeline.splithalfseedconnreproducibility)
        print('Between subject reproducibility: ',betsubj.subject1.ID,'&',betsubj.subject2.ID,': ',betsubj.metric)
    print('Avg between subj reproducibility: ',fixedwf.averagebetweensubjectreproducibility)                    
if len(optimalpipesteps)>0:
    print('-----')
    print('-----')    
    print('Otimized pipelines:')
    for subj in [optimalwf.subjects[0]]:
        for sess in [subj.sessions[0]]:
            for run in [sess.runs[0]]:
                for pipe in run.pipelines:
                    #print(subj.ID,'_',sess.ID,'_',run.seqname, pipe.getsteps())
                    print(run.seqname, pipe.getsteps())
    print('-----')
    print('Otimal pipelines:')
    for subj in optimalwf.subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                print(subj.ID,'_',sess.ID,'_',run.seqname, \
                      'Optimal pipeline:',run.optimalpipeline.getsteps(), \
                      'S-H Reproducibility:',run.optimalpipeline.splithalfseedconnreproducibility)                
    print('-----')
    print('Between subject reproducibility:')
    for betsubj in optimalwf.betweensubjectreproducibility:

        print(betsubj.subject1.ID,'_',betsubj.session1.ID, \
              'Optimal pipeline:',betsubj.run1.optimalpipeline.getsteps(), \
              'S-H Reproducibility:',betsubj.run1.optimalpipeline.splithalfseedconnreproducibility)
        print(betsubj.subject2.ID,'_',betsubj.session2.ID, \
              'Optimal pipeline:',betsubj.run2.optimalpipeline.getsteps(), \
              'S-H Reproducibility:',betsubj.run2.optimalpipeline.splithalfseedconnreproducibility)
        print('Between subject reproducibility: ',betsubj.subject1.ID,'&',betsubj.subject2.ID,': ',betsubj.metric)
    print('Avg between subj reproducibility: ',optimalwf.averagebetweensubjectreproducibility)



