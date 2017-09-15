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

basePath='/home/mkayvanrad/data/healthyvolunteer'
seedatlasfile='/home/mkayvanrad/data/atlas/harvard-oxford_cortical_subcortical_structural/pcc.nii.gz'
atlasfile='/usr/share/data/fsl-mni152-templates/MNI152lin_T1_2mm_brain'
seqname='mbepi'
attnstr='#####'

subjects=[]

for subj in sessions.keys():
    for sess in sessions[subj]:
        fileutils.createdir(basePath+'/'+subj+'/'+sess+'/processed/')
        data=workflow.Data()
        data.bold=basePath+'/'+subj+'/'+sess+'/nii/mbepi.nii.gz'
        if not os.path.exists(data.bold):
            data.bold+=attentionstr
        data.card=basePath+'/'+subj+'/'+sess+'/physio/siemens/3fmri102b'+subj+'.puls.1D'
        if not os.path.exists(data.card):
            data.card+=attentionstr
        data.resp=basePath+'/'+subj+'/'+sess+'/physio/biopac/run3.resp.1D'
        if not os.path.exists(data.resp):
            data.resp+=attentionstr
        data.opath=basePath+'/'+subj+'/'+sess+'/processed'+'/'+seqname
        subject=workflow.Subject(subj)
        session=workflow.Session(sess)
        run=workflow.Run(seqname,data)
        session.addrun(run)
        subject.addsession(session)
        subjects.append(subject)
      
workflow.savesubjects(basePath+'/'+seqname+'_'+'subjects.txt',subjects)

