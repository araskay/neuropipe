# includes functions for working with files/directories used in the pipeline tool.

import os, shutil
import subprocess

def removext(filename):
    noext=os.path.splitext(filename)[0]
    if noext==filename:
        return(noext)
    else:
        return(removext(noext))

def addniigzext(filename):
    if (filename[-4:len(filename)] == '.nii'):
        #print('Input is a file with .nii extension. Cannot add .nii.gz extension')
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
    
def mgztonifti(filename):
    p=subprocess.Popen(['mri_convert',filename,removext(filename)+'.nii.gz'])
    p.communicate()
    os.remove(filename)
    
def unzipnifti(filename):
    p=subprocess.Popen(['fslchfiletype','NIFTI',filename,removext(filename)+'.nii'])
    p.communicate()
    return(removext(filename)+'.nii')
    
def zipnifti(filename):
    p=subprocess.Popen(['fslchfiletype','NIFTI_GZ',filename])
    p.communicate()
    return(removext(filename)+'.nii.gz')

def createdir(dirpath):
    try:
        os.makedirs(dirpath)
    except:
        print('Directory exists. Moving on.')
