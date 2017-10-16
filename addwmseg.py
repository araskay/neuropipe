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
    print('Usage: addwmseg.py --input <input subject file> --output <output subject file> --recondir <recon directory>\nIt is assumed that freesurfer recons for all subjects exist in <recon directory> under <subjID>_<sessID>.')
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        print('Usage: addwmseg.py --input <input subject file> --output <output subject file> --recondir <recon directory>\nIt is assumed that freesurfer recons for all subjects exist in <recon directory> under <subjID>_<sessID>.')
        sys.exit()
    elif opt in ('-i','--input'):
        ifile=arg
    elif opt in ('-o','--output'):
        ofile=arg
    elif opt in ('--recondir'):
        recondir=arg

if ifile=='' or ofile=='' or recondir=='':
    sys.exit('Usage: addwmseg.py --input <input subject file> --output <output subject file> --recondir <recon directory>\nIt is assumed that freesurfer recons for all subjects exist in <recon directory> under <subjID>_<sessID>.')

attentionstr='#####'    
    
recondir=os.path.abspath(recondir) # just to remove possible end slash (/) for consistency

subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            wmseg=recondir+'/'+subj.ID+'_'+sess.ID+'/mri/wm.mgz'
            p=subprocess.Popen(['mri_convert',wmseg,fileutils.removext(run.data.structural)+'_wmseg.nii.gz'])
            p.communicate()
            p=subprocess.Popen(['fslreorient2std',fileutils.removext(run.data.structural)+'_wmseg.nii.gz',fileutils.removext(run.data.structural)+'_wmseg.nii.gz'])
            p.communicate()
            run.data.wmseg=fileutils.removext(run.data.structural)+'_wmseg.nii.gz'
            if (not os.path.exists(run.data.wmseg)) or (not os.path.exists(wmseg)):
                run.data.wmseg+=attentionstr
                
workflow.savesubjects(ofile,subjects)
