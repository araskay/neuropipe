# to implement: the option to keep/discard intermediate steps
import sys
import nibabel
import numpy as np
import seedcorr
import fileutils
import subprocess # used to run bash commands
import os
import spmsim, preprocessingstep

class Pipeline:
    def __init__(self,name,steps):
        self.name=name
        self.steps=steps
        self.ibase=''
        self.obase=''
        self.data=None
        self.keepintermed=False
        self.output=''
        self.pipelinerun=False
        self.pipelinerunsplithalf=False
        self.splithalfoutputs=['','']
        self.splithalfseedconnreproducibility=None
        #self.connectivityseedfile=''
        self.seedconnoutput=''
        self.seedconnoutputmni152=''
        self.envvars=None
    
    def setibase(self,ibase):
        self.ibase=ibase
        
    def setobase(self,obase):
        self.obase=obase
    
    def setdata(self,data):
        self.data=data
    
    def setenvvars(self,envvars):
        self.envvars=envvars
    
    def discardintermediates(self):
        self.keepintermed=False
        
    def keepintermediates(self):
        self.keepintermed=True
        
    #def setconnectivityseedfile(self,seedfile):
    #    self.connectivityseedfile=seedfile
    
    def run(self):
        # first create output directory if necessary
        (directory,namebase)=os.path.split(self.obase)
        fileutils.createdir(directory)
        if len(self.steps)>0:
            stepibase=self.ibase
            stepobase=self.obase
            if len(self.name)>0:
                stepobase+='_'+self.name
            for step in self.steps:
                stepobase+='_'+step.name
                step.setibase(stepibase)
                step.setobase(stepobase)
                step.setdata(self.data)
                step.run()
                stepibase=stepobase
            self.output=stepobase
            # discard intermediates if needed
            if (not self.keepintermed):
                stepibase=self.ibase
                stepobase=self.obase
                if len(self.name)>0:
                    stepobase+='_'+self.name
                for step in self.steps[0:-1]:
                    stepobase+='_'+step.name
                    step.setibase(stepibase)
                    step.setobase(stepobase)
                    step.removeofiles()
                    stepibase=stepobase
        else:
            p=subprocess.Popen(['fslchfiletype','NIFTI_GZ',self.ibase,self.obase+'_'+self.name])
            p.communicate()
            self.output=self.obase+'_'+self.name
        self.pipelinerun=True
                
        
    def runsplithalf(self):
        # get and save pipeline attributes to restore at the end
        ibase=self.ibase
        obase=self.obase
        output=self.output
        pipelinerun=self.pipelinerun
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
        # restore pipeline's original attributes
        self.ibase=ibase
        self.obase=obase
        self.output=output
        self.pipelinerun=pipelinerun
        # set pipelinerunsplithalf to True
        self.pipelinerunsplithalf=True
    
    def calcsplithalfseedconnreproducibility(self):
        # make sure seed file is given
        if (self.data.connseed == ''):
            sys.exit('Error: Need to set a seed file before calling calcsplithalfseedconnreproducibility. Use Pipeline class method setconnectivityseedfile(<seedfilename>).')
        # if runsplithalf not called already, call it now
        if (not self.pipelinerunsplithalf):
            self.runsplithalf()
        # compute seed connectivity maps for each split half
        seedcorr.calcseedcorr(fileutils.addniigzext(self.splithalfoutputs[0]), \
                              fileutils.addniigzext(self.data.connseed), \
                              self.splithalfoutputs[0]+'_seedconn.nii.gz', \
                              1) # p_thresh = 1 (i.e., do not threshold)
        seedcorr.calcseedcorr(fileutils.addniigzext(self.splithalfoutputs[1]), \
                              fileutils.addniigzext(self.data.connseed), \
                              self.splithalfoutputs[1]+'_seedconn.nii.gz', \
                              1) # p_thresh = 1 (i.e., do not threshold)
        # now compute the correlation between r_sh1 and r_sh2
        self.splithalfseedconnreproducibility=spmsim.pearsoncorr(self.splithalfoutputs[0]+'_seedconn_pearsonr.nii.gz', \
                                                                 self.splithalfoutputs[1]+'_seedconn_pearsonr.nii.gz')

    def calcseedconn(self,p_thresh):
        if not self.pipelinerun:
            self.run()
        seedcorr.calcseedcorr(fileutils.addniigzext(self.output), \
                              fileutils.addniigzext(self.data.connseed), \
                              self.output+'_seedconn_thr'+str(p_thresh)+'.nii.gz', \
                              p_thresh)
        self.seedconnoutput=self.output+'_seedconn_thr'+str(p_thresh)+'_pearsonr'
            
    def getsteps(self):
        s=''
        for step in self.steps:
            s=s+' > '+step.name
        return(s)
            
    def seedconn2mni(self):
        # first get transformation parameters on the output of the pipeline
        p=preprocessingstep.PreprocessingStep('tomni152',[])
        p.setenvvars(self.envvars)
        p.setdata(self.data)
        p.setibase(self.output)
        p.setobase(fileutils.removext(self.output)+'_2mni152')
        p.run()
        # then use the parameters to transform the SPM
        p=subprocess.Popen(['flirt','-in',self.seedconnoutput,\
                            '-ref',self.envvars.mni152,\
                            '-applyxfm','-init',self.data.tomni152,\
                            '-out',fileutils.removext(self.seedconnoutput)+'_2mni152'])
        p.communicate()        
        self.seedconnoutputmni152=fileutils.removext(self.seedconnoutput)+'_2mni152.nii.gz'
        
            

            
            
            

