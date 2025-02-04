import numpy as np
import nibabel

# calculate similarity of two SPMs based on Pearson correlation
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

# calculate similarity of two SPMs based on Jaccard index
def jaccardind(spm1file,spm2file):
    # input: 3D SPM files
    # output: Jaccard similarity index between the two SPM's (single number)

    spm1_nib=nibabel.load(spm1file)
    spm1=spm1_nib.get_data()

    spm2_nib=nibabel.load(spm2file)
    spm2=spm2_nib.get_data()    
    
    # first reshape into 1D
    spm1_1D=np.reshape(spm1,(1,np.prod(spm1.shape[0:3])))
    spm2_1D=np.reshape(spm2,(1,np.prod(spm2.shape[0:3])))
    
    # binarize the arrays
    spm1_1D[spm1_1D != 0]=1
    spm2_1D[spm2_1D != 0]=1
    
    # now compute Jaccard similarity index
    return(len(np.where((spm1_1D==1) & (spm2_1D==1))[0])/len(np.where((spm1_1D==1) | (spm2_1D==1))[0]))