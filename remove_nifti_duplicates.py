#!/usr/bin/env python

import workflow, getopt, sys, fileutils

def printhelp():
    print('Usage: remove_nifti_duplicate.py --subjects <subjects file>')
    print('Removes nifti duplicates, which can cause FSL tools to fail.')

ifile=''

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','subjects='])
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

subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            fileutils.remove_nifti_duplicate(run.data.bold)
            fileutils.remove_nifti_duplicate(run.data.brainmask)
            fileutils.remove_nifti_duplicate(run.data.structuralcsf)
            fileutils.remove_nifti_duplicate(run.data.structuralgm)
            fileutils.remove_nifti_duplicate(run.data.structuralwm)
            fileutils.remove_nifti_duplicate(run.data.boldcsf)
            fileutils.remove_nifti_duplicate(run.data.boldgm)
            fileutils.remove_nifti_duplicate(run.data.boldwm)
            fileutils.remove_nifti_duplicate(run.data.boldcsfwm)
