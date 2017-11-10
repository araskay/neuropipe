# this script gets two text files, containing path/name of SPM files to be compared in the two sets (e.g., optimized pipe and fixed pipe) and computes group connectivity for each set, and group variations in connectivity between the two sets. For pre- and post-RETROICOR version use spmstats_prepostRET.py. 

import nibabel,sys
import numpy as np
import scipy.stats
import statsmodels.stats.multitest as mtest
import getopt

p_thresh=0.05

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

def printhelp():
    print('Usage: spmstats --set1 <text file> --set2 <text file> --obase <output base>')

set1=''
set2=''
obase=''
    
# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','set1=', 'set2=','obase='])
except getopt.GetoptError:
    printhelp()
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        printhelp()
        sys.exit()
    elif opt in ('--set1'):
        set1=arg
    elif opt in ('--set2'):
        set2=arg
    elif opt in ('--obase'):
        obase=arg

if set1=='' or set2=='' or obase=='':
    printhelp()
    sys.exit() 

prefiles=[]
postfiles=[]
# the code was originally written for pre- and post- retroicor, and that is where the variable names, prefiles, and postfiles, come from

f1=open(set1)
spm1=f1.readline()
spm1=spm1.rstrip()

f2=open(set2)
spm2=f2.readline()    
spm2=spm2.rstrip()

while len(spm1)>0 and len(spm2)>0:
    prefiles.append(spm1)
    postfiles.append(spm2)
    spm1=f1.readline()
    spm1=spm1.rstrip()
    spm2=f2.readline()
    spm2=spm2.rstrip()

prepostmatchedpairst(prefiles,postfiles,obase+'_groupdiff.nii.gz')

groupnetwork(prefiles,obase+'_group1.nii.gz')
groupnetwork(postfiles,obase+'_group2.nii.gz')
