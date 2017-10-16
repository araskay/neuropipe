#!/usr/bin/env python

import workflow, getopt,sys,fileutils,shutil,os, subprocess

ifile=''
ofile=''

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:',\
                                ['help','input=', 'output='])
except getopt.GetoptError:
    print('Usage: reorientstructural.py -i <input subject file> -o <output subject file>\n Report bugs/issues to M. Aras Kayvanrad (mkayvanrad@research.baycrest.org)')
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        print('Usage: reorientstructural.py -i <input subject file> -o <output subject file>\n Report bugs/issues to M. Aras Kayvanrad (mkayvanrad@research.baycrest.org)')
        sys.exit()
    elif opt in ('-i','--input'):
        ifile=arg
    elif opt in ('-o','--output'):
        ofile=arg

if ifile=='' or ofile=='':
    sys.exit('Usage: reorientstructural.py -i <input subject file> -o <output subject file>\n Report bugs/issues to M. Aras Kayvanrad (mkayvanrad@research.baycrest.org)')
        
subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            p=subprocess.Popen(['fslreorient2std',run.data.structural,fileutils.removext(run.data.structural)+'_reorient'])
            p.communicate()
            run.data.structural=fileutils.removext(run.data.structural)+'_reorient.nii.gz'
            
            
workflow.savesubjects(ofile,subjects)
