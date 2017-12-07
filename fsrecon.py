#!/usr/bin/env python

import workflow, getopt,sys,fileutils,shutil,os, subprocess

def printhelp():
    print('Usage: fsrecon.py --input <input subject file> --output <output subject file> [--directive <freesurfer recon-all directive to be used>]')
    print('Unless input subjects file specifies fsrecondir, freesurfer recon-all is performed and fsrecondir updated in the output subjects file.')
    print('Report bugs/issues to M. Aras Kayvanrad (mkayvanrad@research.baycrest.org)')

ifile=''
ofile=''
directive=''

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:',\
                                ['help','input=', 'output=', 'directive'])
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
    elif opt in ('--directive'):
        directive=arg

if ifile=='' or ofile=='':
    printhelp()
    sys.exit()
        
subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            (opath,oname)=os.path.split(run.data.structural)
            if run.data.fsrecondir=='':
                if directive=='':
                    sys.exit('Please specify freesurfer recon-all directive.')
                p=subprocess.Popen(['recon-all','-sd',opath,'-subjid','__fsrecon','-i',run.data.structural,'-'+directive])
                p.communicate()
                run.data.fsrecondir=opath+'/__fsrecon'
            fsrecondir=recondir=os.path.abspath(run.data.fsrecondir) # just to remove possible end slash (/) for consistency
            p=subprocess.Popen(['mri_convert',fsrecondir+'/mri/brainmask.mgz',\
                                opath+'/'+fileutils.removext(oname)+'_brainmask.nii.gz'])
            p.communicate()
            run.data.structural=opath+'/'+fileutils.removext(oname)+'_brainmask.nii.gz'
            
workflow.savesubjects(ofile,subjects)
