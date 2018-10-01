#!/usr/bin/env python

import workflow, getopt,sys,os

def printhelp():
    print('Usage: addaseg.py --input <input subject file> --output <output subject file> --recondir <recon directory>')
    print('It is assumed that freesurfer recons for all subjects exist in <recon directory> under <subjID>_<sessID>.')
    print('Freesurfer recon folder is also added to the output subject file.')

ifile=''
ofile=''
recondir=''

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:',\
                                ['help','input=', 'output=', 'recondir='])
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
    elif opt in ('--recondir'):
        recondir=arg

if ifile=='' or ofile=='' or recondir=='':
    printhelp()
    sys.exit()

attentionstr='#####'    
    
recondir=os.path.abspath(recondir) # just to remove possible end slash (/) for consistency

subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            run.data.fsrecondir=recondir+'/'+subj.ID+'_'+sess.ID
            if not os.path.exists(run.data.fsrecondir):
                run.data.fsrecondir+=attentionstr
            run.data.aseg=recondir+'/'+subj.ID+'_'+sess.ID+'/mri/aseg.mgz'
            if not os.path.exists(run.data.aseg):
                run.data.aseg+=attentionstr
                
workflow.savesubjects(ofile,subjects,append=False)
