import seedcorr

ifile='/home/mkayvanrad/code/pipeline/temp/mbepi.nii.gz'
ofile='/home/mkayvanrad/code/pipeline/temp/r.nii.gz'
seedfile='/home/mkayvanrad/code/pipeline/temp/pcc_harvard-oxford_mbepispace.nii.gz'

seedcorr.calcseedcorr(ifile, seedfile, ofile)