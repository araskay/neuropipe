import workflow
from pipeline import Pipeline
from preprocessingstep import PreprocessingStep
import fileutils
import preprocessingstep
import sys, getopt

# dictionary of corresponding sessions for Healthy elderly data set
# sessions.keys() gives you all subject IDs
# multiple sessions per subject are added to the lists on the right
sessions=dict()
#sessions['11912']=['20170201']
#sessions['7397']=['20170213']
#sessions['6051']=['20170222']
#sessions['13719']=['20170316']
#sessions['4592']=['20170328']
#sessions['10306']=['20170329']
#sessions['8971']=['20170413']
#sessions['12087']=['20170421']
sessions['12475']=['20170501']
sessions['10724']=['20170526']
#sessions['7334']=['20170605']
#sessions['14804']=['20170608']
#sessions['7982']=['20170612']
#sessions['12420']=['20170615']
#sessions['8060']=['20170628']

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
     
basePath='/home/mkayvanrad/data/healthyelderly'

optimalwf=workflow.Workflow('Optimal Pipe')
fixedwf=workflow.Workflow('Fixed Pipe')

for subj in sessions.keys():
    for sess in sessions[subj]:
        data=workflow.Data()
        data.bold=basePath+'/'+subj+'/'+sess+'/nii/mbepi.nii.gz'
        data.card=basePath+'/'+subj+'/'+sess+'/physio/siemens/3fmri102b'+subj+'.puls.1D'
        data.resp=basePath+'/'+subj+'/'+sess+'/physio/biopac/run3.resp.1D'
        
        # make preprocessing steps
        #afnissmooth=PreprocessingStep('ssmooth',['-fwhm',6])
        #motcor=PreprocessingStep('motcor',[])
        #retroicor=PreprocessingStep('retroicor', ['-ignore','10', '-card',run.data.card,'-resp',run.data.resp])
        
        originalsteps=preprocessingstep.makesteps(pipelinefile,data)
        
        # fixed workflow
        subject=workflow.Subject(subj)
        session=workflow.Session(sess)
        run=workflow.Run('mbepi',data)
        pipe=Pipeline('fixedpipe',originalsteps)
        pipe.setibase(fileutils.removeniftiext(data.bold))
        pipe.setobase('/home/mkayvanrad/code/pipeline/temp/'+subj+'_'+sess)
        pipe.setconnectivityseedfile(basePath+'/'+subj+'/'+sess+'/processed/pcc_harvard-oxford_mbepispace.nii.gz')
        run.addpipeline(pipe)
        session.addrun(run)
        subject.addsession(session)
        fixedwf.addsubject(subject)        
        
        # optimal workflow
        subject=workflow.Subject(subj)
        session=workflow.Session(sess)
        run=workflow.Run('mbepi',data)
        count=0
        for steps in preprocessingstep.permutations(originalsteps):
            count=count+1
            pipe=Pipeline('pipe'+str(count),steps)
            pipe.setibase(fileutils.removeniftiext(data.bold))
            pipe.setobase('/home/mkayvanrad/code/pipeline/temp/'+subj+'_'+sess)
            pipe.setconnectivityseedfile(basePath+'/'+subj+'/'+sess+'/processed/pcc_harvard-oxford_mbepispace.nii.gz')
            run.addpipeline(pipe)
        session.addrun(run)
        subject.addsession(session)
        optimalwf.addsubject(subject)

optimalwf.computebetweensubjectreproducibility('mbepi')
fixedwf.computebetweensubjectreproducibility('mbepi')

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
