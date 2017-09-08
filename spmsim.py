import numpy as np
import nibabel

def pearsoncorr(spm1file,spm2file):
    # input: 3D SPM files
    # output: Pearson correlation between the two SPM's (single number)

    spm1_nib=nibabel.load(spm1file)
    spm1=spm1_nib.get_data()

    spm2_nib=nibabel.load(spm2file)
    spm2=spm2_nib.get_data()    
    
    # first reshape into 1D
    spm1_1D=np.reshape(spm1,(1,np.prod(spm1.shape[0:3])))
    spm2_1D=np.reshape(spm2,(1,np.prod(spm2.shape[0:3])))

    # now compute Pearson correlation coefficient
    return(np.corrcoef(spm1_1D,spm2_1D)[0][1])