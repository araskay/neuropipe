import workflow
from pipeline import Pipeline
from preprocessingstep import PreprocessingStep
import fileutils
import preprocessingstep
import sys, getopt, os

# dictionary of corresponding sessions for Healthy elderly data set
# sessions.keys() gives you all subject IDs
# multiple sessions per subject are added to the lists on the right
sessions=dict()
#sessions['11912']=['20170201']
#sessions['7397']=['20170213']
#sessions['6051']=['20170222']
sessions['13719']=['20170316']
sessions['4592']=['20170328']
sessions['10306']=['20170329']
sessions['8971']=['20170413']
sessions['12087']=['20170421']
sessions['12475']=['20170501']
sessions['10724']=['20170526']
sessions['7334']=['20170605']
sessions['14804']=['20170608']
sessions['7982']=['20170612']
sessions['12420']=['20170615']
sessions['8060']=['20170628']

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hp:',['help','pipeline='])
except getopt.GetoptError:
    print('usage: testbench_workflow.py -p <pipeline text file>')
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        print('usage: testbench_workflow.py -p <pipeline text file>')
        sys.exit()
    elif opt in ('-p','--pipeline'):
        pipelinefile=arg

pipelinefile='/home/mkayvanrad/code/pipeline/temp/pipeline.txt'
pipelinefile2='/home/mkayvanrad/code/pipeline/temp/pipeline2.txt'
        
basePath='/home/mkayvanrad/data/healthyelderly'
seedatlasfile='/home/mkayvanrad/data/atlas/harvard-oxford_cortical_subcortical_structural/pcc.nii.gz'
atlasfile='/usr/share/data/fsl-mni152-templates/MNI152lin_T1_2mm_brain'
seqname='mbepi'

optimalwf=workflow.Workflow('Optimal Pipe')
fixedwf=workflow.Workflow('Fixed Pipe')

for subj in sessions.keys():
    for sess in sessions[subj]:
        data=workflow.Data()
        data.bold=basePath+'/'+subj+'/'+sess+'/nii/mbepi.nii.gz'
        data.structural=basePath+'/'+subj+'/'+sess+'/processed/mprage_swp_brain.nii.gz'
        data.card=basePath+'/'+subj+'/'+sess+'/physio/siemens/3fmri102b'+subj+'.puls.1D'
        data.resp=basePath+'/'+subj+'/'+sess+'/physio/biopac/run3.resp.1D'
        data.opath=basePath+'/'+subj+'/'+sess+'/processed'
        #data.connseed=workflow.makeconnseed(data,seedatlasfile,atlasfile,basePath+'/'+subj+'/'+sess+'/processed/pcc_harvard-oxford_'+seqname+'space')
        data.connseed=basePath+'/'+subj+'/'+sess+'/processed/pcc_harvard-oxford_'+seqname+'space.nii.gz'
        
        originalsteps=preprocessingstep.makesteps(pipelinefile,data)
        originalsteps2=preprocessingstep.makesteps(pipelinefile2,data)
        
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
            pipe=Pipeline('yesretroicor'+str(count),steps)
            pipe.setibase(fileutils.removeniftiext(data.bold))
            pipe.setobase(os.path.abspath(data.opath)+'/'+run.seqname)
            pipe.setconnectivityseedfile(data.connseed)
            run.addpipeline(pipe)
        for steps in preprocessingstep.permutations(originalsteps2):
            count=count+1
            pipe=Pipeline('noretroicor'+str(count),steps)
            pipe.setibase(fileutils.removeniftiext(data.bold))
            pipe.setobase(os.path.abspath(data.opath)+'/'+run.seqname)
            pipe.setconnectivityseedfile(data.connseed)
            run.addpipeline(pipe)            
        session.addrun(run)
        subject.addsession(session)
        optimalwf.addsubject(subject)

workflow.savesubjects(basePath+'/subjects1.txt',fixedwf.subjects)
        
optimalwf.computebetweensubjectreproducibility(seqname)
fixedwf.computebetweensubjectreproducibility(seqname)

print(optimalwf.name,': Optimal Pipelines:')
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
