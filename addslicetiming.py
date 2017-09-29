#!/usr/bin/env python

import workflow, getopt,sys,fileutils,shutil,os, subprocess

ifile=''
ofile=''
sliceorder=''
slicetiming=''

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:',\
                                ['help','input=', 'output=', 'slicetiming=', 'sliceorder='])
except getopt.GetoptError:
    print('Usage: addslicetiming.py -i <input subject file> -o <output subject file> --sliceorder <slice oder file> --slicetiming <slice timing file>\n Report bugs/issues to M. Aras Kayvanrad (mkayvanrad@research.baycrest.org')
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        print('Usage: addslicetiming.py -i <input subject file> -o <output subject file> --sliceorder <slice oder file> --slicetiming <slice timing file>\n Report bugs/issues to M. Aras Kayvanrad (mkayvanrad@research.baycrest.org')
        sys.exit()
    elif opt in ('-i','--input'):
        ifile=arg
    elif opt in ('-o','--output'):
        ofile=arg
    elif opt in ('--sliceorder'):
        sliceorder=arg
    elif opt in ('--slicetiming'):
        slicetiming=arg

if ifile=='' or ofile=='':
    sys.exit('Usage: addslicetiming.py -i <input subject file> -o <output subject file> --sliceorder <slice oder file> --slicetiming <slice timing file>\n Report bugs/issues to M. Aras Kayvanrad (mkayvanrad@research.baycrest.org')
        
subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            run.data.slicetiming=slicetiming
            run.data.sliceorder=sliceorder
            
            
workflow.savesubjects(ofile,subjects)
