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
sessions['7130']=['20140312']
sessions['7934']=['20140207']
sessions['9910']=['20140204']
sessions['10577']=['20140325']
sessions['10649']=['20140316']
sessions['11164']=['20140316']
sessions['11308']=['20140304']
sessions['11494']=['20140311']
sessions['11515']=['20140305']
sessions['11570']=['20140310']
sessions['11672']=['20140318']

basePath='/data/klymene/chen_lab/mkayvanrad/data/healthyvolunteer'
#seedatlasfile='/home/mkayvanrad/data/atlas/harvard-oxford_cortical_subcortical_structural/pcc.nii.gz'
#atlasfile='/usr/share/data/fsl-mni152-templates/MNI152lin_T1_2mm_brain'
seqname='mbepi'
attentionstr='#####'

subjects=[]

for subj in sessions.keys():
    for sess in sessions[subj]:
        fileutils.createdir(basePath+'/'+subj+'/'+sess+'/processed/')
        data=workflow.Data()

        data.bold=basePath+'/'+subj+'/'+sess+'/nii/restingboldWIP770AshortTR.nii.gz'
        if not os.path.exists(data.bold):
            data.bold+=attentionstr

        data.structural=basePath+'/'+subj+'/'+sess+'/nii/SagT1MPRAGE.nii.gz'
        if not os.path.exists(data.structural):
            data.structural+=attentionstr

        data.siemensphysio=basePath+'/'+subj+'/'+sess+'/physio/2fmri102a'+subj
        if not os.path.exists(data.siemensphysio+'.ext'):
            data.siemensphysio+=attentionstr

        data.biopacphysio=basePath+'/'+subj+'/'+sess+'/physio/Biopac/'+subj+'_'+sess+'_02.mat'
        if not os.path.exists(data.biopacphysio):
            data.biopacphysio+=attentionstr

        data.opath=basePath+'/'+subj+'/'+sess+'/processed'+'/'+seqname
        subject=workflow.Subject(subj)
        session=workflow.Session(sess)
        run=workflow.Run(seqname,data)
        session.addrun(run)
        subject.addsession(session)
        subjects.append(subject)
      
workflow.savesubjects(basePath+'/'+seqname+'_'+'subjects.txt',subjects)

