# to implement: the option to keep/discard intermediate steps
import sys
import nibabel
import numpy as np
import seedcorr
import fileutils
import subprocess # used to run bash commands
import os

class Pipeline:
    def __init__(self,name,steps):
        self.name=name
        self.steps=steps
        self.keepintermed=False
        self.output=''
        self.pipelinerunsplithalf=False
        self.splithalfoutputs=['','']
        self.splithalfseedconnreproducibility=None
        self.connectivityseedfile=''
    
    def setibase(self,ibase):
        self.ibase=ibase
        
    def setobase(self,obase):
        self.obase=obase
        
    def discardintermediates(self):
        self.keepintermed=False
        
    def keepintermediates(self):
        self.keepintermed=True
        
    def setconnectivityseedfile(self,seedfile):
        self.connectivityseedfile=seedfile
    
    def run(self):
        stepibase=self.ibase
        stepobase=self.obase+'_'+self.name
        for step in self.steps:
            stepobase=stepobase+'_'+step.name
            step.setibase(stepibase)
            step.setobase(stepobase)
            step.run()
            stepibase=stepobase
        self.output=stepobase
        # discard intermediates if needed
        if (not self.keepintermed):
            stepibase=self.ibase
            stepobase=self.obase+'_'+self.name
            for step in self.steps[0:-1]:
                stepobase=stepobase+'_'+step.name
                step.setibase(stepibase)
                step.setobase(stepobase)
                step.removeofiles()
                stepibase=stepobase

                
        
    def runsplithalf(self):
        # get and save pipeline parameters to restore at the end
        ibase=self.ibase
        obase=self.obase
        output=self.output
        # read input and split it into half
        img_nib=nibabel.load(fileutils.addniigzext(ibase))
        img=img_nib.get_data()
        affine=img_nib.affine
        hdr=img_nib.header
        # split image into halves
        img_sh1=img[:,:,:,0:int(img.shape[3]/2)]
        img_sh2=img[:,:,:,int(img.shape[3]/2):img.shape[3]]
        # write img_sh1 and img_sh2 in separate nifti files
        onifti = nibabel.nifti1.Nifti1Image(img_sh1,affine,hdr)
        onifti.to_filename(obase+'_splithalf1.nii.gz')
        #
        onifti = nibabel.nifti1.Nifti1Image(img_sh2,affine,hdr)
        onifti.to_filename(obase+'_splithalf2.nii.gz')
        # run the pipeline on the first split-half
        self.ibase=obase+'_splithalf1'
        self.obase=obase+'_splithalf1'
        self.run()
        self.splithalfoutputs[0]=self.output
        # run the pipeline on the second split-half
        self.ibase=obase+'_splithalf2'
        self.obase=obase+'_splithalf2'
        self.run()
        self.splithalfoutputs[1]=self.output
        # restore pipeline's original ibase, obase, and output
        self.ibase=ibase
        self.obase=obase
        self.output=output
        # set pipelinerunsplithalf to True
        self.pipelinerunsplithalf=True
    
    def calcsplithalfseedconnreproducibility(self):
        # make sure seed file is given
        if (self.connectivityseedfile == ''):
            sys.exit('Error: Need to set a seed file before calling calcsplithalfseedconnreproducibility. Use Pipeline class method setconnectivityseedfile(<seedfilename>).')
        # if runsplithalf not called already, call it now
        if (not self.pipelinerunsplithalf):
            self.runsplithalf()
        # compute seed connectivity maps for each split half
        r_sh1=seedcorr.calcseedcorr(fileutils.addniigzext(self.splithalfoutputs[0]), \
                                    fileutils.addniigzext(self.connectivityseedfile), \
                                    self.splithalfoutputs[0]+'_seedconn.nii.gz')
        r_sh2=seedcorr.calcseedcorr(fileutils.addniigzext(self.splithalfoutputs[1]), \
                                    fileutils.addniigzext(self.connectivityseedfile), \
                                    self.splithalfoutputs[1]+'_seedconn.nii.gz')
        # now compute the correlation between r_sh1 and r_sh2
        # first reshape into 1D
        r_sh1_1D=np.reshape(r_sh1,(1,np.prod(r_sh1.shape[0:3])))
        r_sh2_1D=np.reshape(r_sh2,(1,np.prod(r_sh2.shape[0:3])))
        # now compute Pearson correlation coefficient
        self.splithalfseedconnreproducibility=np.corrcoef(r_sh1_1D,r_sh2_1D)[0][1]
        
            
        
        
        
        
        
            

            
            
            

