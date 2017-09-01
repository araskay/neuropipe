import nibabel
import numpy as np
import sys

def calcseedcorr(ifile, seedfile, ofile):
    # compute seed-based correlation coefficients
    # ifile: input 4D fMRI data file name (e.g., epi.nii.gz)
    # seedfile: file containing 3D data of binary seed ROI in functional space
    # ofile: file to which the resulting correlation coefficient are written
    
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
    
    # compute Pearson correlations wrt mean time series
    for i in np.arange(np.prod(img.shape[0:3])):
        if (np.std(imgreshape[i,:]) != 0):
            r_1D[i]=np.corrcoef(meants,imgreshape[i,:])[0][1]
    
    # reshape to 3D
    r=np.reshape(r_1D,(img.shape[0],img.shape[1],img.shape[2]))
    
    # write r to NIFTI file
    onifti = nibabel.nifti1.Nifti1Image(r,affine)
    onifti.to_filename(ofile)
    
    # also return r as the function output
    return r
    
    
    
            