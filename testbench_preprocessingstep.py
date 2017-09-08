from preprocessingstep import PreprocessingStep

p=PreprocessingStep('brainExtractAFNI',[])

p.setibase('/home/mkayvanrad/code/pipeline/temp/mbepi')
p.setobase('/home/mkayvanrad/code/pipeline/temp/mbepi_beAFNI')

p.run()

