volname='/home/mkayvanrad/scratch/spikecore/TBR01_PHA_FBN1319_0017_mcflirt_brainExtractAFNI.nii';
maskname='/home/mkayvanrad/scratch/spikecore/TBR01_PHA_FBN1319_0017_mcflirt_brainExtractAFNI__brainmask.nii';
mpename='/home/mkayvanrad/scratch/spikecore/TBR01_PHA_FBN1319_0017_mcflirt.par'
outprefix='/home/mkayvanrad/scratch/spikecore/myspikecor'
OUT_PARAM='volume';
interpname='/home/mkayvanrad/scratch/spikecore/TBR01_PHA_FBN1319_0017_mcflirt_brainExtractAFNI_myspikecor';

output=spikecor(volname, maskname, mpename, outprefix, OUT_PARAM, interpname);
