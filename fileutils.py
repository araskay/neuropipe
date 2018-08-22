# includes functions for working with files/directories used in the pipeline tool.

import os, shutil
import subprocess

def removefile(filename):
    if os.path.exists(filename):
        os.remove(filename)

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
    # input: file name without extension or +orig/+tlrc
    # also removes the afni after conversion
    if os.path.exists(filename+'+orig.HEAD'):
        process=subprocess.Popen(['3dAFNItoNIFTI', '-prefix', filename+'.nii', '-overwrite', filename+'+orig'])
        (output,error)=process.communicate()
        process=subprocess.Popen(['gzip', '-f', filename+'.nii'])
        (output,error)=process.communicate()
        # remove afni files- it is important since most AFNI functions do not overwrite existing files
        removefile(filename+'+orig.HEAD')
        removefile(filename+'+orig.BRIK')
    elif os.path.exists(filename+'+tlrc.HEAD'):
        process=subprocess.Popen(['3dAFNItoNIFTI', '-prefix', filename+'.nii', '-overwrite', filename+'+tlrc'])
        (output,error)=process.communicate()
        process=subprocess.Popen(['gzip', '-f', filename+'.nii'])
        (output,error)=process.communicate()
        # remove afni files- it is important since most AFNI functions do not overwrite existing files
        removefile(filename+'+tlrc.HEAD')
        removefile(filename+'+tlrc.BRIK')
        
def mgztonifti(filename):
    p=subprocess.Popen(['mri_convert',filename,removext(filename)+'.nii.gz'])
    p.communicate()
    removefile(filename)
    
def unzipnifti(filename):
    if os.path.exists(removext(filename)+'.nii.gz') and os.path.exists(removext(filename)+'.nii'):
        removefile(removext(filename)+'.nii')
    p=subprocess.Popen(['fslchfiletype','NIFTI',filename,removext(filename)+'.nii'])
    p.communicate()
    return(removext(filename)+'.nii')
    
def zipnifti(filename):
    if not os.path.exists(removext(filename)+'.nii'):
        sys.exit('Error in zipnifti: file '+removext(filename)+'.nii does not exist.')
    if os.path.exists(removext(filename)+'.nii.gz') and os.path.exists(removext(filename)+'.nii'):
        removefile(removext(filename)+'.nii.gz')
    p=subprocess.Popen(['gzip',removext(filename)+'.nii'])
    p.communicate()
    return(removext(filename)+'.nii.gz')

def createdir(dirpath):
    try:
        os.makedirs(dirpath)
    except:
        print('Directory exists. Moving on.')
