#!/usr/bin/env python

import workflow, getopt,sys,os

def printhelp():
    print('Usage: removefsrecon.py --input <input subject file> --output <output subject file>')
    print('Removes entries for --fsrecondir and --aseg fields in the subjects file.')

ifile=''
ofile=''

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:',\
                                ['help','input=', 'output='])
except getopt.GetoptError:
    printhelp()
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        printhelp()
        sys.exit()
    elif opt in ('-i','--input'):
        ifile=arg
    elif opt in ('-o','--output'):
        ofile=arg

if ifile=='' or ofile=='':
    printhelp()
    sys.exit()

subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            run.data.fsrecondir=''
            run.data.aseg=''
                
workflow.savesubjects(ofile,subjects)
