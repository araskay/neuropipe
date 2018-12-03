# Includes functions for working with files/directories used in the pipeline tool.

import os, shutil
import subprocess
import sys

# remove a file
def removefile(filename):
    if os.path.exists(filename):
        os.remove(filename)

# remove file extention and return base name (incl. path)
def removext(filename):
    noext=os.path.splitext(filename)[0]
    if noext==filename:
        return(noext)
    else:
        return(removext(noext))

def namebase(filename):
    (directory,namebase)=os.path.split(filename)
    namebase=removext(namebase)
    return(namebase)

# add .nii.gz extension to the file name and return the new file name
# This does NOT compress the file- merely adds an extension
# if the input has .nii extension, the input file name is returned unchanged
def addniigzext(filename):
    if (filename[-4:len(filename)] == '.nii'):
        #print('Input is a file with .nii extension. Cannot add .nii.gz extension')
        return(filename)
    elif (filename[-7:len(filename)] != '.nii.gz'):
        return(filename+'.nii.gz')
    else:
        return(filename)

# remove nifti extension(.nii or .nii.gz) from file name.
def removeniftiext(filename):
    if (filename[-4:len(filename)] == '.nii'):
        return(filename[0:-4])
    elif (filename[-7:len(filename)] == '.nii.gz'):
        return(filename[0:-7])
    else:
        return(filename)
    
# convert afni file format to nifti (zipped)
# also removes the afni after conversion
def afni2nifti(filename):
    # input: file name without extension or +orig/+tlrc
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

# convert mgz file format to nifti
# also removes the mgz file after conversion
def mgztonifti(filename):
    p=subprocess.Popen(['mri_convert',filename,removext(filename)+'.nii.gz'])
    p.communicate()
    removefile(filename)

# remove duplicate nifti files, where both .nii and .nii.gz files exists with the same base name
def remove_nifti_duplicate(filename,removeunzip=True):
    if removeunzip:
        if os.path.exists(removext(filename)+'.nii.gz') and os.path.exists(removext(filename)+'.nii'):
            removefile(removext(filename)+'.nii')
    else:
        if os.path.exists(removext(filename)+'.nii.gz') and os.path.exists(removext(filename)+'.nii'):
            removefile(removext(filename)+'.nii.gz')

# unzip nifti file
def unzipnifti(filename):
    if len(filename)>0:
        remove_nifti_duplicate(filename)
        p=subprocess.Popen(['fslchfiletype','NIFTI',filename,removext(filename)+'.nii'])
        p.communicate()
        return(removext(filename)+'.nii')
    else:
        return(filename)

# zip nifti file
def zipnifti(filename):
    remove_nifti_duplicate(filename,removeunzip=False)
    if not os.path.exists(removext(filename)+'.nii'):
        sys.exit('Error in zipnifti: file '+removext(filename)+'.nii does not exist.')
    p=subprocess.Popen(['gzip',removext(filename)+'.nii'])
    p.communicate()
    return(removext(filename)+'.nii.gz')

# create directory.
# if the directory exists, a warning message is printed.
def createdir(dirpath):
    try:
        os.makedirs(dirpath)
    except:
        print('Directory exists. Moving on.')
