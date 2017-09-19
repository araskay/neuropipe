from preprocessingstep import PreprocessingStep
import workflow

mni152='/usr/share/data/fsl-mni152-templates/MNI152lin_T1_2mm_brain'
envvars=workflow.EnvVars()
envvars.mni152=mni152

data=workflow.Data()
data.structural='/home/mkayvanrad/code/pipeline/temp/mprage_swp_brain.nii.gz'

p=PreprocessingStep('tomni152',[])
p.setenvvars(envvars)
p.setdata(data)

p.setibase('/home/mkayvanrad/code/pipeline/temp/mbepi')
p.setobase('/home/mkayvanrad/code/pipeline/temp/mbepi_2mni')

p.run()

