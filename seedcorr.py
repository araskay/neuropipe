import nibabel
import numpy as np
import sys
import scipy.stats
import fileutils
import statsmodels.stats.multitest as mtest

# NOT USED- demeaning has no effect on Pearson R- just used this function to test this.
def demean(s):
    return(s-np.mean(s))

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
        sys.exit('In calcseedcorr: {} and {} do not match in dimension.'.format(ifile,seedfile))
            
    imgreshape=img.reshape(np.prod(img.shape[0:3]),img.shape[3])
    seedreshape=seed.reshape(np.prod(seed.shape[0:3]),1)
    
    # compute mean time series
    meants=np.mean(imgreshape[np.where(seedreshape == 1)[0], :], axis=0)
    
    # check meants
    if (np.std(meants) == 0):
        print('WARNING: mean time series over seed ROI has zero standard deviation')
    
    r_1D=np.zeros(np.prod(img.shape[0:3]))
    #t_1D=np.zeros(np.prod(img.shape[0:3]))
    z_1D=np.zeros(np.prod(img.shape[0:3]))
    p_1D=np.zeros(np.prod(img.shape[0:3]))
    n=img.shape[3]
    
    # compute Pearson correlations wrt mean time series
    for i in np.arange(np.prod(img.shape[0:3])):
        if (np.std(imgreshape[i,:]) != 0):
            #(r_1D[i],p_1D[i])=scipy.stats.pearsonr(meants,imgreshape[i,:])
            #t_1D[i]=r_1D[i]*np.sqrt((len(meants)-2)/(1-r_1D[i]*r_1D[i]))
            # use Fisher transformation to compute a z-score and p-value
            r_1D[i]=np.corrcoef(meants,imgreshape[i,:])[0][1]
            fr=1/2*np.log((1+r_1D[i])/(1-r_1D[i]))
            z_1D[i]=fr*np.sqrt(n-3)
            p_1D[i]=2*(1-scipy.stats.norm.cdf(abs(z_1D[i])))
            
    p_1D_fdr=mtest.multipletests(p_1D,p_thresh,'fdr_bh')
                
    # reshape to 3D
    r=np.reshape(r_1D,(img.shape[0],img.shape[1],img.shape[2]))
    z=np.reshape(z_1D,(img.shape[0],img.shape[1],img.shape[2]))
    p_adj=np.reshape(p_1D_fdr[1],(img.shape[0],img.shape[1],img.shape[2]))
    #p=np.reshape(p_1D,(img.shape[0],img.shape[1],img.shape[2]))
    
    # write r to NIFTI file
    onifti = nibabel.nifti1.Nifti1Image(r,affine)
    onifti.to_filename(fileutils.removeniftiext(obase)+'_r.nii.gz')

    # write t to NIFTI file
    onifti = nibabel.nifti1.Nifti1Image(z,affine)
    onifti.to_filename(fileutils.removeniftiext(obase)+'_z.nii.gz')

    # now threshold r and z
    r_1D[~p_1D_fdr[0]]=0
    z_1D[~p_1D_fdr[0]]=0    

    # reshape to 3D
    r=np.reshape(r_1D,(img.shape[0],img.shape[1],img.shape[2]))
    z=np.reshape(z_1D,(img.shape[0],img.shape[1],img.shape[2]))
    
    # write r to NIFTI file
    onifti = nibabel.nifti1.Nifti1Image(r,affine)
    onifti.to_filename(fileutils.removeniftiext(obase)+'_r_thresh.nii.gz')

    # write t to NIFTI file
    onifti = nibabel.nifti1.Nifti1Image(z,affine)
    onifti.to_filename(fileutils.removeniftiext(obase)+'_z_thresh.nii.gz')
    
    
    # write p_adj to NIFTI file
    onifti = nibabel.nifti1.Nifti1Image(p_adj,affine)
    onifti.to_filename(fileutils.removeniftiext(obase)+'_p_adj.nii.gz')
    
    # write p to NIFTI file
    #onifti = nibabel.nifti1.Nifti1Image(p,affine)
    #onifti.to_filename(fileutils.removeniftiext(obase)+'_p.nii.gz')    
    
    return((fileutils.removeniftiext(obase)+'_r.nii.gz',fileutils.removeniftiext(obase)+'_z.nii.gz',fileutils.removeniftiext(obase)+'_r_thresh.nii.gz',fileutils.removeniftiext(obase)+'_z_thresh.nii.gz',fileutils.removeniftiext(obase)+'_p_adj.nii.gz'))
    

            