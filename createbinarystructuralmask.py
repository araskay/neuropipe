#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 14:39:54 2018

@author: mkayvanrad
"""

import workflow, getopt,sys,os,fileutils,subprocess

def printhelp():
    print('Usage: createbinarystructuralmask.py --input <input subject file> --output <output subject file>')
    print('Binarize the sturctural image and update the --structuralbinarymask field in the output subjects file with the resulting binary mask.')
    print('NOTE: The structural image must be a skull-stripped image.')

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
            (opath,oname)=os.path.split(run.data.structural)
            # add structural brain mask
            p=subprocess.Popen(['fslmaths',\
                                run.data.structural,\
                                '-bin',\
                                opath+'/'+fileutils.removext(oname)+'_bin.nii.gz'])
            p.communicate()
            run.data.structuralbrainmask=opath+'/'+fileutils.removext(oname)+'_bin.nii.gz'            

workflow.savesubjects(ofile,subjects,append=False)
