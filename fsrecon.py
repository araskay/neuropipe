#!/usr/bin/env python

import workflow, getopt,sys,fileutils,shutil,os, subprocess

def printhelp():
    print('Usage: fsrecon.py --input <input subject file> --output <output subject file> [--directive <freesurfer recon-all directive to be used>]')
    print('Unless input subjects file specifies fsrecondir, freesurfer recon-all is performed and fsrecondir updated in the output subjects file.')
    print('The structural field of the subjects file is updated to the nifti-converted fs recon-all brain extracted structural.')
    print('Default directive is autorecon-all')
    print('Report bugs/issues to M. Aras Kayvanrad (mkayvanrad@research.baycrest.org)')

ifile=''
ofile=''
directive='all'

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','input=', 'output=', 'directive='])
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
                
                # if output directory exists, delete it first, otherwise recon-all throws an error
                if os.path.exists(opath+'/'+fileutils.removext(oname)+'_fsrecon'):
                    p=subprocess.Popen(['rm','-r',opath+'/'+fileutils.removext(oname)+'_fsrecon'])
                    p.communicate()

                p=subprocess.Popen(['recon-all','-sd',opath,'-subjid',fileutils.removext(oname)+'_fsrecon','-i',run.data.structural,'-'+directive])
                p.communicate()
                run.data.fsrecondir=opath+'/'+fileutils.removext(oname)+'_fsrecon'
            elif not os.path.exists(run.data.fsrecondir):
                sys.exit('Error in Subject '+subj.ID+' Session '+sess.ID+': --fsrecondir is not empty but point to a non-existet directory.')
            fsrecondir=os.path.abspath(run.data.fsrecondir) # just to remove possible end slash (/) for consistency
            p=subprocess.Popen(['mri_convert',fsrecondir+'/mri/brainmask.mgz',\
                                opath+'/'+fileutils.removext(oname)+'_brainmask.nii.gz'])
            p.communicate()
            run.data.structural=opath+'/'+fileutils.removext(oname)+'_brainmask.nii.gz'
            run.data.aseg=run.data.fsrecondir+'/mri/aseg.mgz'
            
            # add structural brain mask
            p=subprocess.Popen(['fslmaths',\
                                opath+'/'+fileutils.removext(oname)+'_brainmask.nii.gz',\
                                '-bin',\
                                opath+'/'+fileutils.removext(oname)+'_binarybrainmask.nii.gz'])
            p.communicate()
            run.data.structuralbrainmask=opath+'/'+fileutils.removext(oname)+'_binarybrainmask.nii.gz'

workflow.savesubjects(ofile,subjects)
