#!/bin/bash

function mni152probabilistic2funcspacebinseed {

# this scripts transforms a probabilistic ROI (atlas) on MNI152 into a binary seed mask on the subject-specific functional space. Used, for example, for generating binary seed masks for OPPNI SCONN analysis.
# need to have write access in the current directory as some temp files are created.

funcim=$1 # subject specific functional image- can be just a "raw" (i.e., unprocessed) nifti
structim=$2 # brain extracted volume without extension, e.g., mprage_swp_bet
nvol=$3 # number of volumes, i.e., measurements- the one in the middle used as ref
atlas=$4 # atlas file
obase=$5 # output base path/name


let refvol=$nvol/2 # use the middle volume as reference

# extract brain mask from a temporal mean volume and apply to 4D data
fslmaths ${funcim} -Tmean _temp_tmean # temporal mean
bet2 _temp_tmean _temp_tmean  -f 0.3 -n -m # create a binary mask from the the mean image. (bet2 automatically adds a _mask suffix to the output file)
fslmaths ${funcim} -mas _temp_tmean_mask _temp_bet # use the mask to brain extract the 4D functional data

# calculate registration parameters
fslroi _temp_bet _temp_bet_refvol refvol 1 # use the middle volume as reference
flirt -in _temp_bet_refvol -ref ${structim} -out _temp_func2struct -omat _temp_func2struct.mat -dof 7
#convert_xfm -inverse -omat ${obase}_struct2func.mat ${obase}_func2struct.mat
flirt -ref /usr/share/data/fsl-mni152-templates/MNI152lin_T1_2mm_brain -in ${structim} -out _temp_struct2mni -omat _temp_struct2mni.mat -dof 12 # on chegs the mni templates are located at /software/fsl/data/standard/MNI152lin_T1_2mm_brain
#convert_xfm -inverse -omat ${obase}_mni2struct.mat ${obase}_struct2mni.mat
convert_xfm -omat _temp_func2mni.mat -concat _temp_struct2mni.mat _temp_func2struct.mat
convert_xfm -inverse -omat _temp_mni2func.mat _temp_func2mni.mat

# now use the transformation matrix to transfrom the atlas to subject-specific functional space
flirt -in ${atlas} -applyxfm -init _temp_mni2func.mat -out ${obase} -paddingsize 0.0 -interp trilinear -ref _temp_bet_refvol

# threshold at 50% and binarize
fslmaths ${obase} -thr 50 -bin ${obase}

# flirt -in ${structim}_pve_wm -applyxfm -init ${obase}_struct2func.mat -out ${obase}_tc_mc_bet_refvol_pve_wm -paddingsize 0.0 -interp trilinear -ref ${obase}_tc_mc_bet_refvol

rm _temp*

}

mni152probabilistic2funcspacebinseed $1 $2 $3 $4 $5
