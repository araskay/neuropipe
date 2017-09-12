from preprocessingstep import PreprocessingStep

p=PreprocessingStep('3dFourier',['-highpass','0.01','-ignore','0'])

p.setibase('/home/mkayvanrad/code/pipeline/temp/mbepi')
p.setobase('/home/mkayvanrad/code/pipeline/temp/mbepi_HPF')

p.run()

