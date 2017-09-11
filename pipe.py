import workflow
from pipeline import Pipeline
from preprocessingstep import PreprocessingStep
import fileutils
import preprocessingstep
import sys, getopt, os

subjectsfiles=[]
pipelinefiles=[]
combs=[]

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hp:s:',\
                                ['help','pipeline=', 'subjects=', 'perm=', 'onoff=', 'fixed='])
except getopt.GetoptError:
    print('usage: testbench_workflow.py -p <pipeline text file> -s <subjects file>')
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        print('usage: testbench_workflow.py -p <pipeline text file> -s <subjects file>')
        sys.exit()
    elif opt in ('-p','--pipeline'):
        pipelinefiles.append(arg)
    elif opt in ('--perm'):
        combs.append(['perm',arg])
    elif opt in ('--onoff'):
        combs.append(['onoff',arg])
    elif opt in ('--fixed'):
        combs.append(['fixed',arg])
    elif opt in ('-s','--subjects'):
        subjectsfiles.append(arg)
# run workflow
if len(pipelinefiles)>0:
    runwf=workflow.Workflow('Run Pipe')
    subjects=[]
    for subjectfile in subjectfiles:
        subjects=subjects+workflow.getsubjects(subjectfile)
    for subj in subjects:
        for sess in subj:
            for run in sess.runs:
                steps=[]
                for pipelinefile in pipelinefiles:
                    steps=steps+preprocessingstep.makesteps(pipelinefile,run.data)
                pipe=Pipeline('runpipe',steps)
                pipe.setibase(run.data.bold)
                pipe.setobase(run.data.opath)
                pipe.setconnectivityseedfile(run.data.connseed)
                run.addpipeline(pipe)
        runwf.addsubject(subj)

# optimal workflow
if len(combs)>0:
    optimalwf=workflow.Workflow('Optimal Pipe')
    subjects=[]
    for subjectfile in subjectfiles:
        subjects=subjects+workflow.getsubjects(subjectfile)
    for subj in subjects:
        for sess in subj:
            for run in sess.runs:
                stepscombinationslist=[]
                for l in combs:
                    if l[0]='perm':
                        steps=preprocessingstep.makesteps(l[1],run.data)
                        stepscombinationslist=preprocessingstep.concatstepslists(stepscombinationslist,list(preprocessingstep.permutations(steps)))
                    elif l[0]='onoff':
                        steps=preprocessingstep.makesteps(l[1],run.data)
                        stepscombinationslist=preprocessingstep.concatstepslists(stepscombinationslist,list(preprocessingstep.onoff(steps)))
                    elif l[0]='fixed':
                        steps=preprocessingstep.makesteps(l[1],run.data)
                        stepscombinationslist=preprocessingstep.concatstepslists(stepscombinationslist,[steps])
                count=0
                for steps in stepscombinationslist:
                    count=count+1
                    pipe=Pipeline('pipe'+str(count),steps)
                    pipe.setibase(run.data.bold)
                    pipe.setobase(run.data.opath)
                    pipe.setconnectivityseedfile(run.data.connseed)
                    run.addpipeline(pipe)
        optimalwf.addsubject(subj)
# fixed workflow
    fixedwf=workflow.Workflow('Fixed Pipe')
    subjects=[]
    for subjectfile in subjectfiles:
        subjects=subjects+workflow.getsubjects(subjectfile)
    for subj in subjects:
        for sess in subj:
            for run in sess.runs:
                fixedsteps=[]
                for l in combs:
                    steps=preprocessingstep.makesteps(l[1],run.data)
                    fixedsteps=fixedsteps+steps
                pipe=Pipeline('fixedpipe',steps)
                pipe.setibase(run.data.bold)
                pipe.setobase(run.data.opath)
                pipe.setconnectivityseedfile(run.data.connseed)
                run.addpipeline(pipe)
        fixedwf.addsubject(subj)
# now process
if len(pipelinefiles)>0:
    runwf.process()

if len(combs)>0:
    optimalwf.computebetweensubjectreproducibility(seqname)
    fixedwf.computebetweensubjectreproducibility(seqname)

    print(optimalwf.name,':')
    for betsubj in optimalwf.betweensubjectreproducibility:
        print(betsubj.subject1.ID,'_',betsubj.session1.ID, \
              'Optimal pipeline:',betsubj.run1.optimalpipeline.getsteps(), \
              'S-H Reproducibility:',betsubj.run1.optimalpipeline.splithalfseedconnreproducibility)
        print(betsubj.subject2.ID,'_',betsubj.session2.ID, \
              'Optimal pipeline:',betsubj.run2.optimalpipeline.getsteps(), \
              'S-H Reproducibility:',betsubj.run2.optimalpipeline.splithalfseedconnreproducibility)
        print('Between subject reproducibility: ',betsubj.subject1.ID,'&',betsubj.subject2.ID,': ',betsubj.metric)
    print('Avg between subj reproducibility: ',optimalwf.averagebetweensubjectreproducibility)

    print(fixedwf.name,':')
    for betsubj in fixedwf.betweensubjectreproducibility:
        print(betsubj.subject1.ID,'_',betsubj.session1.ID, \
              'Optimal pipeline:',betsubj.run1.optimalpipeline.getsteps(), \
              'S-H Reproducibility:',betsubj.run1.optimalpipeline.splithalfseedconnreproducibility)
        print(betsubj.subject2.ID,'_',betsubj.session2.ID, \
              'Optimal pipeline:',betsubj.run2.optimalpipeline.getsteps(), \
              'S-H Reproducibility:',betsubj.run2.optimalpipeline.splithalfseedconnreproducibility)
        print('Between subject reproducibility: ',betsubj.subject1.ID,'&',betsubj.subject2.ID,': ',betsubj.metric)
    print('Avg between subj reproducibility: ',fixedwf.averagebetweensubjectreproducibility)
