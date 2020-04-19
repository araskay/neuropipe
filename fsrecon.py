#!/usr/bin/env python

import getopt,sys,shutil,os, subprocess, distutils.spawn

# check if pipe.py is accessible and if yes,
# add pipe.py directory to path before loading other modules
if distutils.spawn.find_executable('pipe.py') == None:
    print('Cannot find pipe.py. Possible causes/solutions:')
    print('- Make sure the installation directory is added to the path')
    print('- Alternatively you can run directly from the installation directory.')
    sys.exit()
sys.path.insert(0,os.path.dirname(distutils.spawn.find_executable('pipe.py')))

import workflow, fileutils

def printhelp():
    print(('Usage: fsrecon.py --input <input subject file>'
           ' --output <output subject file>'
           ' [--directive <freesurfer recon-all directive to be used>]'
           ' [--reorient]'))
    print('Unless input subjects file specifies fsrecondir, freesurfer recon-all is performed and fsrecondir updated in the output subjects file.')
    print('The structural field of the subjects file is updated to the nifti-converted fs recon-all brain extracted structural.')
    print('Default directive is autorecon-all')


ifile=''
ofile=''
directive='all'
reorient = False

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',
                                ['help','input=', 'output=',
                                 'directive=',
                                 'reorient'])
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
    elif opt in ('--reorient'):
        reorient=True

if ifile=='' or ofile=='':
    printhelp()
    sys.exit()
        
subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            (opath,oname)=os.path.split(run.data.structural)
            
            # if fs recon dir not give, run fs recon-all
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
            
            # if given fs recon dir does not exists, exit
            elif not os.path.exists(run.data.fsrecondir):
                sys.exit('Error in Subject '+subj.ID+' Session '+sess.ID+': --fsrecondir is not empty but point to a non-existet directory.')

            # just to remove possible end slash (/) for consistency
            run.data.fsrecondir = os.path.abspath(run.data.fsrecondir)

            run.data.structural = fileutils.mgztonifti(
                run.data.fsrecondir+'/mri/brainmask.mgz'
            )

            run.data.aseg = fileutils.mgztonifti(
                run.data.fsrecondir+'/mri/aseg.mgz'
            )

            if reorient:
                run.data.structural = fileutils.reorient2std(
                    run.data.structural
                )
                run.data.aseg = fileutils.reorient2std(
                    run.data.aseg
                )

            # add structural brain mask
            p=subprocess.Popen(
                [
                    'fslmaths',
                    run.data.structural,
                    '-bin',
                    fileutils.removext(run.data.structural)+'_mask.nii.gz'
                ]
            )
            p.communicate()

            run.data.structuralbrainmask = (
                fileutils.removext(run.data.structural)+'_mask.nii.gz'
            )
                

workflow.savesubjects(ofile,subjects)
