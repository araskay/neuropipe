import workflow
data=workflow.Data()
data.bold='/home/mkayvanrad/code/pipeline/temp/mbepi.nii.gz'
data.structural='/home/mkayvanrad/code/pipeline/temp/mprage_swp_brain.nii.gz'
data.opath='/home/mkayvanrad/code/pipeline/temp/'

seedatlasfile='/home/mkayvanrad/data/atlas/harvard-oxford_cortical_subcortical_structural/pcc.nii.gz'
atlasfile='/usr/share/data/fsl-mni152-templates/MNI152lin_T1_2mm_brain'

workflow.makeconnseed(data,seedatlasfile,atlasfile,'pcc')