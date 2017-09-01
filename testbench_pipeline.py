from preprocessingstep import PreprocessingStep
from pipeline import Pipeline

ibase='/home/mkayvanrad/code/pipeline/temp/mbepi'
obase='/home/mkayvanrad/code/pipeline/temp/mbepi'
seedfile='/home/mkayvanrad/code/pipeline/temp/pcc_harvard-oxford_mbepispace.nii.gz'

mcflirt=PreprocessingStep('mcflirt',[])
seedconn=PreprocessingStep('seedconn',[seedfile])
steps=[mcflirt,seedconn]

pipe1=Pipeline('pipe1',steps)
pipe1.setibase(ibase)
pipe1.setobase(obase)

#pipe1.setconnectivityseedfile(seedfile)
#pipe1.calcsplithalfseedconnreproducibility()
#print(pipe1.splithalfseedconnreproducibility)

pipe1.run()


