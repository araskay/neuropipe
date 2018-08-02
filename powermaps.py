#!/usr/bin/env python

# THIS IS INCOMPLETE. USE MATBAL VERSION INSTEAD.
# this script gets a subjects file and generates cardiac, respiratory, and low-frequency power maps.

import workflow, getopt,sys,fileutils,shutil,os, subprocess, nibabel
import numpy as np

def printhelp():
    print('Usage: powermaps.py --subjects <input subject file> [--ndiscard <number of frames to discard at the beginning of the time series> = 0]')
    print('This script generates cardiac, respiratory, and low-frequency power maps.')
    print('Report bugs/issues to M. Aras Kayvanrad (mkayvanrad@research.baycrest.org)')

ifile=''
ndiscard=0

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','subjects=','ndiscard='])
except getopt.GetoptError:
    printhelp()
    sys.exit()

for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        printhelp()
        sys.exit()
    elif opt in ('--subjects'):
        ifile=arg

if ifile=='':
    printhelp()
    sys.exit()

ifile = '/home/mkayvanrad/scratch/subjects.txt'

subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:

            img_nib=nibabel.load(run.data.bold)
            img=img_nib.get_data()
            affine=img_nib.affine # used to save the result in a NIFTI file
            hdr=img_nib.header # also used to save the result

            img = img[:,:,:,ndiscard-1:-1]
            
            F = np.fft.fft(img, axis=-1)
            
            


            p=subprocess.Popen(['fslreorient2std',run.data.structural,fileutils.removext(run.data.structural)+'_reorient'])
            p.communicate()
            run.data.structural=fileutils.removext(run.data.structural)+'_reorient.nii.gz'
            
            
workflow.savesubjects(ofile,subjects)
