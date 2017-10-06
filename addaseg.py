#!/usr/bin/env python

import workflow, getopt,sys,fileutils,shutil,os, subprocess

ifile=''
ofile=''
recondir=''

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:',\
                                ['help','input=', 'output=', 'recondir='])
except getopt.GetoptError:
    print('Usage: addaseg.py --input <input subject file> --output <output subject file> --recondir <recon directory>\nIt is assumed that freesurfer recons for all subjects exist in <recon directory> under <subjID>_<sessID>.')
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        print('Usage: addaseg.py --input <input subject file> --output <output subject file> --recondir <recon directory>\nIt is assumed that freesurfer recons for all subjects exist in <recon directory> under <subjID>_<sessID>.')
        sys.exit()
    elif opt in ('-i','--input'):
        ifile=arg
    elif opt in ('-o','--output'):
        ofile=arg
    elif opt in ('--recondir'):
        recondir=arg

if ifile=='' or ofile=='' or recondir=='':
    sys.exit('Usage: addaseg.py --input <input subject file> --output <output subject file> --recondir <recon directory>\nIt is assumed that freesurfer recons for all subjects exist in <recon directory> under <subjID>_<sessID>.')

attentionstr='#####'    
    
recondir=os.path.abspath(recondir) # just to remove possible end slash (/) for consistency

subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            run.data.aseg=recondir+'/'+subj.ID+'_'+sess.ID+'/mri/aseg.mgz'
            if not os.path.exists(run.data.aseg):
                run.data.aseg+=attentionstr
                
workflow.savesubjects(ofile,subjects)
