# this script gets two text files, containing path/name of SPM files to be compared in the two sets (e.g., optimized pipe and fixed pipe) and computes group connectivity for each set, and group variations in connectivity between the two sets. For pre- and post-RETROICOR version use spmstats_prepostRET.py. 

import nibabel,sys
import numpy as np
import scipy.stats
import statsmodels.stats.multitest as mtest
import getopt, os, fileutils

def prepostmatchedpairst(prespmfiles,postspmfiles,ofile,p_thresh,correction):
    
    n=len(prespmfiles)
    
    # the following just to get the size of the SPMs
    img_nib=nibabel.load(prespmfiles[0])
    img=img_nib.get_data()
    affine=img_nib.affine # used to save the result in a NIFTI file
    hdr=img_nib.header # also used to save the result

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
    if correction=='none':
        t[p>p_thresh]=np.nan
    else:  
        p_fdr=mtest.multipletests(p,p_thresh,correction)    
        t[~p_fdr[0]]=np.nan


    # write t to file
    t=np.reshape(t,(img.shape[0],img.shape[1],img.shape[2]))
    onifti = nibabel.nifti1.Nifti1Image(t,affine,header=hdr)
    onifti.to_filename(ofile)

def groupnetwork(spmfiles,ofile,p_thresh,correction):

    n=len(spmfiles)
    
    # the following just to get the size of the SPMs
    img_nib=nibabel.load(spmfiles[0])
    img=img_nib.get_data()
    affine=img_nib.affine # used to save the result in a NIFTI file
    hdr=img_nib.header # also used to save the result

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
    if correction=='none':
        t[p>p_thresh]=np.nan
    else:  
        p_fdr=mtest.multipletests(p,p_thresh,correction)    
        t[~p_fdr[0]]=np.nan


    # write t to file
    t=np.reshape(t,(img.shape[0],img.shape[1],img.shape[2]))
    onifti = nibabel.nifti1.Nifti1Image(t,affine,header=hdr)
    onifti.to_filename(ofile)
    
def groupaverage(spmfiles,ofile):

    n=len(spmfiles)
    
    # the following just to get the size of the SPMs
    img_nib=nibabel.load(spmfiles[0])
    img=img_nib.get_data()
    affine=img_nib.affine # used to save the result in a NIFTI file
    hdr=img_nib.header # also used to save the result

    stats=np.zeros(img.shape)
    
    for i in np.arange(n):
        spm1_nib=nibabel.load(spmfiles[i])
        spm1=spm1_nib.get_data()
        stats+=spm1

    stats = stats/n

    # write t to file
    onifti = nibabel.nifti1.Nifti1Image(stats,affine,header=hdr)
    onifti.to_filename(ofile)    

def printhelp():
    print('Usage: spmstats --set1 <text file> --set2 <text file> --obase <output base> [--p <p-value> (default=0.05) --correction <correction method> (default=bonferroni) --groupaverage]')
    print('If two spm sets provided, group inference for each set (t-test), and group inference for variations between the two sets (set2-set1), i.e., matched-pairs t-test, are performed. If only one spm set provided, group inference for that set is performed.')
    print('If --groupaverage used, in addition to group inference (t-test), group average is calculated for each set given.')
    print('correction methods:')
    print('bonferroni: one-step correction')
    print('sidak: one-step correction')
    print('holm-sidak: step down method using Sidak adjustments')
    print('holm: step-down method using Bonferroni adjustments')
    print('simes-hochberg: step-up method  (independent)')
    print('hommel: closed method based on Simes tests (non-negative)')
    print('fdr_bh: Benjamini/Hochberg  (non-negative)')
    print('fdr_by: Benjamini/Yekutieli (negative)')
    print('fdr_tsbh: two stage fdr correction (non-negative)')
    print('fdr_tsbky: two stage fdr correction (non-negative)')
    print('none: no correction (only threshold p-values)')

p_thresh=0.05 
correction='bonferroni'
set1=''
set2=''
obase=''
grpavg=False
    
# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','set1=', 'set2=','obase=', 'p=', 'correction=', 'groupaverage'])
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
    elif opt in ('--p'):
        p_thresh=float(arg)
    elif opt in ('--correction'):
        correction=arg
    elif opt in ('--groupaverage'):
        grpavg=True

if obase=='':
    printhelp()
    sys.exit()

if set1=='' and set2=='':
    printhelp()
    sys.exit() 

prefiles=[]
postfiles=[]
# the code was originally written for pre- and post- retroicor, and that is where the variable names, prefiles, and postfiles, come from

# the following used to save results
(directory,namebase)=os.path.split(set1)
set1namebase=fileutils.removext(namebase)
(directory,namebase)=os.path.split(set2)
set2namebase=fileutils.removext(namebase)

if len(set1)>0:
    f1=open(set1)
    spm1=f1.readline()
    spm1=spm1.rstrip()

    while len(spm1)>0:
        prefiles.append(spm1)
        spm1=f1.readline()
        spm1=spm1.rstrip()

if len(set2)>0:
    f2=open(set2)
    spm2=f2.readline()    
    spm2=spm2.rstrip()

    while len(spm2)>0:
        postfiles.append(spm2)
        spm2=f2.readline()
        spm2=spm2.rstrip()

if len(set1)>0 and len(set2)>0:
    prepostmatchedpairst(prefiles,postfiles,obase+'_matchedpairs_'+set1namebase+'_'+set2namebase+'.nii.gz',p_thresh,correction)
if len(set1)>0:
    groupnetwork(prefiles,obase+'_group_'+set1namebase+'.nii.gz',p_thresh,correction)
    if grpavg:
        groupaverage(prefiles,obase+'_groupaverage_'+set1namebase+'.nii.gz')
if len(set2)>0:
    groupnetwork(postfiles,obase+'_group_'+set2namebase+'.nii.gz',p_thresh,correction)
    if grpavg:
        groupaverage(postfiles,obase+'_groupaverage_'+set2namebase+'.nii.gz')
