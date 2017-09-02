from preprocessingstep import PreprocessingStep
from pipeline import Pipeline

ibase='/home/mkayvanrad/code/pipeline/temp/mbepi'
obase='/home/mkayvanrad/code/pipeline/temp/mbepi'
seedfile='/home/mkayvanrad/code/pipeline/temp/pcc_harvard-oxford_mbepispace.nii.gz'

mcflirt=PreprocessingStep('mcflirt',[])
seedconn=PreprocessingStep('seedconn',['-seed',seedfile,'spm_thresh',0.05])
afnissmooth=PreprocessingStep('ssmooth',['-fwhm',6])
motcor=PreprocessingStep('motcor',[])
retroicor=PreprocessingStep('retroicor',['-ignore','10','-card','/home/mkayvanrad/code/pipeline/temp/3fmri102b12475.puls.1D','-resp','/home/mkayvanrad/code/pipeline/temp/run3.resp.1D']);

steps=[retroicor]

pipe1=Pipeline('pipe1',steps)
pipe1.setibase(ibase)
pipe1.setobase(obase)

#pipe1.setconnectivityseedfile(seedfile)
#pipe1.calcsplithalfseedconnreproducibility()
#print(pipe1.splithalfseedconnreproducibility)

pipe1.run()



