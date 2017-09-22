import nibabel
import numpy as np
import sys
import scipy.stats
import fileutils

def calcseedcorr(ifile, seedfile, obase, p_thresh):
    # compute seed-based correlation coefficients
    # ifile: input 4D fMRI data file name (e.g., epi.nii.gz)
    # seedfile: file containing 3D data of binary seed ROI in functional space
    # obase: base file name to which the resulting correlation coefficient are written
    
    img_nib=nibabel.load(ifile)
    img=img_nib.get_data()
        
    seed_nib=nibabel.load(seedfile)
    seed=seed_nib.get_data()
    affine=seed_nib.affine # used to save the result in a NIFTI file
    
    # check to make sure seed image has the right dimensions
    if (not img.shape[0:3] == seed.shape[0:3]):
        sys.exit('Error: {} and {} do not match in dimension.'.format(ifile,seedfile))
            
    imgreshape=img.reshape(np.prod(img.shape[0:3]),img.shape[3])
    seedreshape=seed.reshape(np.prod(seed.shape[0:3]),1)
    
    # compute mean time series
    meants=np.mean(imgreshape[np.where(seedreshape == 1)[0], :], axis=0)
    
    # check meants
    if (np.std(meants) == 0):
        sys.exit('Error: seed file needs to contain a binary ROI')
    
    r_1D=np.zeros(np.prod(img.shape[0:3]))
    t_1D=np.zeros(np.prod(img.shape[0:3]))
    p_1D=np.zeros(np.prod(img.shape[0:3]))
    
    # compute Pearson correlations wrt mean time series
    for i in np.arange(np.prod(img.shape[0:3])):
        if (np.std(imgreshape[i,:]) != 0):
            (r_1D[i],p_1D[i])=scipy.stats.pearsonr(meants,imgreshape[i,:])
            t_1D[i]=r_1D[i]*np.sqrt((len(meants)-2)/(1-r_1D[i]*r_1D[i]))
            if (p_1D[i] > p_thresh):
                r_1D[i]=0
                t_1D[i]=0
                p_1D[i]=0
                
    # reshape to 3D
    r=np.reshape(r_1D,(img.shape[0],img.shape[1],img.shape[2]))
    t=np.reshape(t_1D,(img.shape[0],img.shape[1],img.shape[2]))
    p=np.reshape(p_1D,(img.shape[0],img.shape[1],img.shape[2]))
    
    # write r to NIFTI file
    onifti = nibabel.nifti1.Nifti1Image(r,affine)
    onifti.to_filename(fileutils.removeniftiext(obase)+'_pearsonr.nii.gz')

    # write t to NIFTI file
    onifti = nibabel.nifti1.Nifti1Image(t,affine)
    onifti.to_filename(fileutils.removeniftiext(obase)+'_tval.nii.gz')
    
    # also return r, t, p as the function output
    return (r,t,p)
    

            