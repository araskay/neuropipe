from preprocessingstep import PreprocessingStep

mcflirt=PreprocessingStep('mcflirt','')

mcflirt.setibase('/home/mkayvanrad/code/pipeline/temp/mbepi')
mcflirt.setobase('/home/mkayvanrad/code/pipeline/temp/mbepi_mc')

mcflirt.run()

