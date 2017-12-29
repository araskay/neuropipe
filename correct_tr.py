#!/usr/bin/env python

import workflow, getopt,sys,fileutils,shutil,os, subprocess, nibabel

def printhelp():
    print('Usage: correct_tr.py --subjects <subjects file> --tr <TR>')
    
subjectsfile=''
tr=''

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','subjects=', 'tr='])
except getopt.GetoptError:
    printhelp()
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        printhelp()
        sys.exit()
    elif opt in ('--subjects'):
        subjectsfile=arg
    elif opt in ('--tr'):
        tr=arg


if subjectsfile=='' or tr=='':
    printhelp()
    sys.exit()

subjects=workflow.getsubjects(subjectsfile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            img_nib=nibabel.load(fileutils.addniigzext(run.data.bold))
            zooms=img_nib.header.get_zooms()
            zooms=list(zooms) # convert to list to enable changing values
            print(subj.ID,'_',sess.ID,'_',run.seqname,'Original TR =',zooms[-1], 'changed to',tr)
            zooms[-1]=float(tr)
            img_nib.header.set_zooms(zooms)
            img_nib.to_filename(fileutils.addniigzext(run.data.bold))
                
