#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, getopt, os
import distutils.spawn
import numpy as np
import nibabel as nib

# check if pipe.py is accessible and if yes,
# add pipe.py directory to path before loading neuropipe modules
if distutils.spawn.find_executable('pipe.py') == None:
    sys.exit('Please install Neuropipe before running this utility.')
sys.path.insert(0,os.path.dirname(distutils.spawn.find_executable('pipe.py')))

import workflow, fileutils

def downsamp_array(x: np.array, q: int, axis: int = -1) -> np.array:
    '''
    down-sample x by a factor of q along the given axis.
    
    Parameters
    ----------
    x: array_like
        the data to be down-sampled
    q: int
        down-sampling factor
    axis: int, optional
        the axis of x that is down-sampled
    
    Returns
    -------
    resampled_x: array_like
        the resampled array
        
    '''
    resampled_x = np.take(x, np.arange(x.shape[axis])[::q], axis = axis)
    return resampled_x

def printhelp():
    '''
    print terminal help message
    '''
    print('\n------')
    print(('Usage: downsamp.py --in <input subjects file>'
           ' --out <output subjects file>'
           ' --factor <under-sampling factor>'))
    print('------\n')

def main(in_fname: str, out_fname: str, q: int) -> None:
    subjects = workflow.getsubjects(in_fname)
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                # read nifti
                img_nib = nib.load(fileutils.addniigzext(run.data.bold))
                img = img_nib.get_fdata()
                hdr = img_nib.header
                aff = img_nib.affine

                # downsample and update header
                img = downsamp_array(img,q)
                zooms = list(hdr.get_zooms())
                zooms[-1] *= q # update TR
                hdr.set_zooms(zooms)

                # save downsampled image to nifti and update subjects
                out_nib = nib.nifti1.Nifti1Image(img, affine=aff, header=hdr)
                dec_fname = fileutils.add_suffix_nifti(run.data.bold,'_dec'+str(q))
                out_nib.to_filename(dec_fname)
                run.data.bold = dec_fname

    workflow.savesubjects(out_fname,subjects)

if __name__ == '__main__':
    # parse command-line arguments
    in_fname=''
    out_fname=''
    q = None
    try:
        (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                    ['help','in=', 'out=', 'factor='])
    except getopt.GetoptError:
        printhelp()
        sys.exit()
    for (opt,arg) in opts:
        if opt in ('-h', '--help'):
            printhelp()
            sys.exit()
        elif opt in ('--in'):
            in_fname=arg
        elif opt in ('--out'):
            out_fname=arg
        elif opt in ('--factor'):
            q = int(arg)

    if in_fname=='' or out_fname=='' or q is None:
        printhelp()
        sys.exit()

    if q<1:
        sys.exit('Error: factor must be >=1')

    main(in_fname, out_fname, q)     

 