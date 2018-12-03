#!/usr/bin/env python

import workflow, getopt,sys,fileutils,shutil,os, subprocess

def printhelp():
    print('Usage: updateopath.py --input <input subject file> --output <output subject file> --opath <opath> [--prefix <prefix> --addsessions]')
    print('If --addsessions, each subject\'s opath is updated as <opath>/<subjID>/<sessID>/[<prefix>]')
    
ifile=''
ofile=''
opath=''
prefix=''
addsessions=False

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','input=', 'output=', 'opath=','addsessions'])
except getopt.GetoptError:
    printhelp()
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        printhelp()
        sys.exit()
    elif opt in ('--input'):
        ifile=arg
    elif opt in ('--output'):
        ofile=arg
    elif opt in ('--opath'):
        opath=arg
    elif opt in ('--prefix'):
        prefix=arg
    elif opt in ('--addsessions'):
        addsessions=True

if ifile=='' or ofile=='' or opath=='':
    printhelp()
    sys.exit()

opath=os.path.abspath(opath) # just to remove possible end slash (/) for consistency

subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            if addsessions:
                run.data.opath=opath+'/'+subj.ID+'/'+sess.ID+'/'+prefix
            else:
                run.data.opath=opath
                
workflow.savesubjects(ofile,subjects,append=False)
