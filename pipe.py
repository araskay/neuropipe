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

if len(combs)>0:
    optimalwf=workflow.Workflow('Optimal Pipe')
    fixedwf=workflow.Workflow('Fixed Pipe')
    subjects=[]
    for subjectfile in subjectfiles:
        subjects=subjects+workflow.getsubjects(subjectfile)
    for subj in subjects:
        for sess in subj:
            for run in sess.runs:
                steps=[]
                for l in combs:
                    if l[0]='perm':
                        steps=steps+list(preprocessingstep.permutations(preprocessingstep.makesteps(pipelinefile,run.data))
                    steps=steps+preprocessingstep.makesteps(pipelinefile,run.data)
            pipe=Pipeline('runpipe',steps)
                pipe.setibase(run.data.bold)
                pipe.setobase(run.data.opath)
                pipe.setconnectivityseedfile(run.data.connseed)
                run.addpipeline(pipe)
    runwf.addsubject(subj)

for subj in subjects:
    for sess in subj:
        '''data=workflow.Data()
        data.bold=basePath+'/'+subj+'/'+sess+'/nii/mbepi.nii.gz'
        data.structural=basePath+'/'+subj+'/'+sess+'/processed/mprage_swp_brain.nii.gz'
        data.card=basePath+'/'+subj+'/'+sess+'/physio/siemens/3fmri102b'+subj+'.puls.1D'
        data.resp=basePath+'/'+subj+'/'+sess+'/physio/biopac/run3.resp.1D'
        data.opath=basePath+'/'+subj+'/'+sess+'/processed'
        data.connseed=workflow.makeconnseed(data,seedatlasfile,atlasfile,basePath+'/'+subj+'/'+sess+'/processed/pcc_harvard-oxford_'+seqname+'space')'''
        for run in sess.runs:
        
        
        
        originalsteps=preprocessingstep.makesteps(pipelinefile,data)
        
        # fixed workflow
        subject=workflow.Subject(subj)
        session=workflow.Session(sess)
        run=workflow.Run(seqname,data)
        pipe=Pipeline('fixedpipe',originalsteps)
        pipe.setibase(fileutils.removeniftiext(data.bold))
        pipe.setobase(os.path.abspath(data.opath)+'/'+run.seqname)
        pipe.setconnectivityseedfile(data.connseed)
        run.addpipeline(pipe)
        session.addrun(run)
        subject.addsession(session)
        fixedwf.addsubject(subject)        
        
        # optimal workflow
        subject=workflow.Subject(subj)
        session=workflow.Session(sess)
        run=workflow.Run(seqname,data)
        count=0
        for steps in preprocessingstep.permutations(originalsteps):
            count=count+1
            pipe=Pipeline('pipe'+str(count),steps)
            pipe.setibase(fileutils.removeniftiext(data.bold))
            pipe.setobase(os.path.abspath(data.opath)+'/'+run.seqname)
            pipe.setconnectivityseedfile(data.connseed)
            run.addpipeline(pipe)
        session.addrun(run)
        subject.addsession(session)
        optimalwf.addsubject(subject)

workflow.savesubjects(basePath+'/subjects1.txt',fixedwf.subjects)
workflow.savesubjects(basePath+'/subjects2.txt',fixedwf.subjects)
        
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
