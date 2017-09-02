import os
import subprocess

def addniigzext(filename):
    if (filename[-4:len(filename)] == '.nii'):
        print('Input is a file with .nii extension. Cannot add .nii.gz extension')
        return(filename)
    elif (filename[-7:len(filename)] != '.nii.gz'):
        return(filename+'.nii.gz')
    else:
        return(filename)

def removeniftiext(filename):
    if (filename[-4:len(filename)] == '.nii'):
        return(filename[0:-4])
    elif (filename[-7:len(filename)] == '.nii.gz'):
        return(filename[0:-7])
    else:
        return(filename)
    
    
def afni2nifti(filename):
    # file name without extension or +orig
    # also removes the afni after conversion
    process=subprocess.Popen(['3dAFNItoNIFTI', '-prefix', filename, filename+'+orig'])
    (output,error)=process.communicate()
    process=subprocess.Popen(['gzip', '-f', filename+'.nii'])
    (output,error)=process.communicate()
    # remove afni files- it is important since most AFNI functions do not overwrite existing files
    os.remove(filename+'+orig.HEAD')
    os.remove(filename+'+orig.BRIK')    