# contains functions to do stats on SPMs

import nibabel,sys
import numpy as np
import scipy.stats
import statsmodels.stats.multitest as mtest
import workflow, subprocess, fileutils

p_thresh=0.01

def prepostmatchedpairst(prespmfiles,postspmfiles,ofile):
    
    n=len(prespmfiles)
    
    # the following just to get the size of the SPMs
    img_nib=nibabel.load(prespmfiles[0])
    img=img_nib.get_data()
    affine=img_nib.affine # used to save the result in a NIFTI file

    paireddiff=np.zeros((n,np.prod(img.shape)))
    t=np.zeros((1,np.prod(img.shape)))    
    p=np.zeros((1,np.prod(img.shape)))
    
    for i in np.arange(n):
        spm1_nib=nibabel.load(prespmfiles[i])
        spm1=spm1_nib.get_data()
        spm1=spm1.reshape((1,np.prod(spm1.shape)))
        
        spm2_nib=nibabel.load(postspmfiles[i])
        spm2=spm2_nib.get_data()
        spm2=spm2.reshape((1,np.prod(spm2.shape)))
        
        paireddiff[i,:]=spm2-spm1
         
    (t,p)=scipy.stats.ttest_1samp(paireddiff,0.0)
    
    # adjust for multiple comparisons    
    p_fdr=mtest.multipletests(p,p_thresh,'fdr_bh')    
    #t[~p_fdr[0]]=0
    t[p>p_thresh]=np.nan

    # write t to file
    t=np.reshape(t,(img.shape[0],img.shape[1],img.shape[2]))
    onifti = nibabel.nifti1.Nifti1Image(t,affine)
    onifti.to_filename(ofile)

def groupnetwork(spmfiles,ofile):

    n=len(spmfiles)
    
    # the following just to get the size of the SPMs
    img_nib=nibabel.load(spmfiles[0])
    img=img_nib.get_data()
    affine=img_nib.affine # used to save the result in a NIFTI file

    stats=np.zeros((n,np.prod(img.shape)))
    t=np.zeros((1,np.prod(img.shape)))    
    p=np.zeros((1,np.prod(img.shape)))
    
    for i in np.arange(n):
        spm1_nib=nibabel.load(spmfiles[i])
        spm1=spm1_nib.get_data()
        spm1=spm1.reshape((1,np.prod(spm1.shape)))
                
        stats[i,:]=spm1
         
    (t,p)=scipy.stats.ttest_1samp(stats,0.0)
    
    # adjust for multiple comparisons    
    p_fdr=mtest.multipletests(p,p_thresh,'fdr_bh')    
    t[~p_fdr[0]]=np.nan
    #t[p>p_thresh]=np.nan

    # write t to file
    t=np.reshape(t,(img.shape[0],img.shape[1],img.shape[2]))
    onifti = nibabel.nifti1.Nifti1Image(t,affine)
    onifti.to_filename(ofile)
    
        
# dictionary of corresponding sessions for healthy volunteer data set
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

basepath='/home/hpc3820/data/healthyvolunteer/processed/retroicorpipe'
subjectsfile='/home/hpc3820/data/healthyvolunteer/fepi_subjects_checked_physio_skullstrip_reorient_connseedcordinates_aseg_registrations_connseed.txt'
ofile=basepath+'/r_prepostmatchedpairst.nii.gz'
mni152='/u1/work/hpc3194/apps/fsl/data/standard/MNI152_T1_2mm_brain'

prefiles=[]
postfiles=[]
spmfiles=[]

subjects=workflow.getsubjects(subjectsfile)

# first transform r files to mni
for subj in subjects:
    for sess in subj.sessions:
        psdfile=basepath+'/'+subj.ID+'/'+sess.ID+'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_r.nii.gz'
        p=subprocess.Popen(['flirt', '-in', psdfile,\
                            '-applyxfm', '-init', sess.runs[0].data.func2mni,\
                            '-out', fileutils.removext(psdfile)+'_'+'mni152',\
                            '-ref', mni152])
        p.communicate()
              
        
        psdfile=basepath+'/'+subj.ID+'/'+sess.ID+'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_r.nii.gz'
        p=subprocess.Popen(['flirt', '-in', psdfile,\
                            '-applyxfm', '-init', sess.runs[0].data.func2mni,\
                            '-out', fileutils.removext(psdfile)+'_'+'mni152',\
                            '-ref', mni152])
        p.communicate()
                    
print('Registration Done. Now doing stats')

for subj in sessions.keys():
    for sess in sessions[subj]:
        prefiles.append(basepath+'/'+subj+'/'+sess+'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_r_mni152.nii.gz')
        postfiles.append(basepath+'/'+subj+'/'+sess+'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_r_mni152.nii.gz')
        
prepostmatchedpairst(prefiles,postfiles,ofile)

groupnetwork(prefiles,basepath+'/r_pregroupnetwork.nii.gz')
groupnetwork(postfiles,basepath+'/r_postgroupnetwork.nii.gz')


