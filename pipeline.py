# to implement: the option to keep/discard intermediate steps
import sys
import nibabel
import seedcorr
import fileutils
import subprocess # used to run bash commands
import os
import spmsim
import copy

p_thresh=0.05 # significance level for thresholding seed connectivity maps

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
        self.splithalfseedconnoverlap=None
        self.seedconnr=''
        self.seedconnrthresh=''
        self.seedconnz=''
        self.seedconnzthresh=''
        self.seedconnrmni152=''
        self.seedconnrthreshmni152=''
        self.seedconnzmni152=''
        self.seedconnzthreshmni152=''
        self.seedcov=''
        self.seedcovmni152=''
        self.variance=''
        self.variancemni152=''
        self.parcellated=False
        self.seedconncomputed=False
        self.meantscomputed=False
    
    def setibase(self,ibase):
        self.ibase=ibase
        
    def setobase(self,obase):
        self.obase=obase
    
    def setdata(self,data):
        self.data=data
    
    def discardintermediates(self):
        self.keepintermed=False
        
    def keepintermediates(self):
        self.keepintermed=True
        
    def run(self):
        # first create output directory if necessary
        (directory,namebase)=os.path.split(self.obase)
        fileutils.createdir(directory)
        # remove duplicate inputs (if both nii and nii.gz exist)
        fileutils.remove_nifti_duplicate(self.ibase)
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
            if len(self.name)>0:
                p=subprocess.Popen(['fslchfiletype','NIFTI_GZ',self.ibase,fileutils.removext(self.obase)+'_'+self.name])
                p.communicate()
                self.output=fileutils.removext(self.obase)+'_'+self.name
            else:
                p=subprocess.Popen(['fslchfiletype','NIFTI_GZ',self.ibase,fileutils.removext(self.obase)])
                p.communicate()
                self.output=fileutils.removext(self.obase)               
        self.pipelinerun=True
        self.data.bold=self.output        
        
    def runsplithalf(self):
        # first create output directory if necessary
        (directory,namebase)=os.path.split(self.obase)
        fileutils.createdir(directory)        
        # get and save pipeline attributes to restore at the end
        ibase=self.ibase
        obase=self.obase
        output=self.output
        pipelinerun=self.pipelinerun
        data=copy.deepcopy(self.data)
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
        self.data=data
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
        (sh1r,sh1z,sh1rthresh,sh1zthresh,sh1padj,sh1cov,sh1var)=seedcorr.calcseedcorr(fileutils.addniigzext(self.splithalfoutputs[0]), fileutils.addniigzext(self.data.connseed), self.splithalfoutputs[0], p_thresh)
        (sh2r,sh2z,sh2rthresh,sh2zthresh,sh2padj,sh2cov,sh2var)=seedcorr.calcseedcorr(fileutils.addniigzext(self.splithalfoutputs[1]), fileutils.addniigzext(self.data.connseed), self.splithalfoutputs[1], p_thresh)
        
        # split-half reproducibility
        self.splithalfseedconnreproducibility=spmsim.pearsoncorr(sh1z, sh2z)
        # split-half overlap
        self.splithalfseedconnoverlap=spmsim.jaccardind(sh1zthresh, sh2zthresh)
        
    def calcseedconn(self,p_thresh):
        if not self.pipelinerun:
            self.run()
        (self.seedconnr,self.seedconnz,self.seedconrthresh,self.seedconnzthresh,padj,self.seedcov,self.variance)=seedcorr.calcseedcorr(fileutils.addniigzext(self.output), fileutils.addniigzext(self.data.connseed),self.output, p_thresh)
        
        self.seedconnrmni152=''
        self.seedconnrthreshmni152=''
        self.seedconnzmni152=''
        self.seedconnzthreshmni152=''
        self.seedcovmni152=''
        self.variancemni152=''
        
        self.seedconncomputed=True
    
    def getsteps(self):
        s=''
        for step in self.steps:
            s=s+' > '+step.name
        return(s)
    
    def printpipe(self):
        print(self.name,self.getsteps())
        print('S-H reproducibility:',self.splithalfseedconnreproducibility)
        print('S-H overlap:',self.splithalfseedconnoverlap)
        
    
    def output2mni(self):
        if not self.pipelinerun:
            self.run()
        self.data.transform_func2mni()
        
        
    def seedconn2mni(self):
        if self.seedconnr=='' or self.seedconnz=='':
            sys.exit('Error in seedconn2mni: Seed connectivity not computed. Need to call calcseedconn first')
        # first get transformation parameters on the output of the pipeline
      
        self.data.transform_func2mni()

        # then use the parameters to transform the SPMs

        p=subprocess.Popen(['flirt','-in',self.seedconnz,\
                            '-ref',self.data.envvars.mni152,\
                            '-applyxfm','-init',self.data.func2mni,\
                            '-out',fileutils.removext(self.seedconnz)+'_mni152'])
        p.communicate()
        self.seedconnzmni152=fileutils.removext(self.seedconnz)+'_mni152.nii.gz'

        p=subprocess.Popen(['flirt','-in',self.seedconnzthresh,\
                            '-ref',self.data.envvars.mni152,\
                            '-applyxfm','-init',self.data.func2mni,\
                            '-out',fileutils.removext(self.seedconnzthresh)+'_mni152'])
        p.communicate()
        self.seedconnzthreshmni152=fileutils.removext(self.seedconnzthresh)+'_mni152.nii.gz'
        
        p=subprocess.Popen(['flirt','-in',self.seedcov,\
                            '-ref',self.data.envvars.mni152,\
                            '-applyxfm','-init',self.data.func2mni,\
                            '-out',fileutils.removext(self.seedcov)+'_mni152'])
        p.communicate()
        self.seedcovmni152=fileutils.removext(self.seedcov)+'_mni152.nii.gz'
        
        p=subprocess.Popen(['flirt','-in',self.variance,\
                            '-ref',self.data.envvars.mni152,\
                            '-applyxfm','-init',self.data.func2mni,\
                            '-out',fileutils.removext(self.variance)+'_mni152'])
        p.communicate()
        self.variancemni152=fileutils.removext(self.variance)+'_mni152.nii.gz'

    def output2structural(self):
        if not self.pipelinerun:
            self.run()
        self.data.transform_func2struct()

    def parcellate(self):
        if not self.pipelinerun:
            self.run()
        self.data.parcellate_bold()
        self.parcellated=True
        
        
    def meants(self):
        if self.data.boldcsf=='' or self.data.boldgm=='' or self.data.boldwm=='':
            self.parcellate()
        self.data.calc_meants()
        self.meantscomputed=True
