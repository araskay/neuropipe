# to implement: the option to keep/discard intermediate steps
import sys
import nibabel
import numpy as np
import seedcorr
import fileutils
import subprocess # used to run bash commands
import os
import spmsim, preprocessingstep

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
        #self.connectivityseedfile=''
        self.seedconnr=''
        self.seedconnrthresh=''
        self.seedconnz=''
        self.seedconnzthresh=''
        self.seedconnrmni152=''
        self.seedconnrthreshmni152=''
        self.seedconnzmni152=''
        self.seedconnzthreshmni152=''
        self.envvars=None
        self.parcellated=False
        self.seedconncomputed=False
        self.meantscomputed=False
    
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
                step.setenvvars(self.envvars)
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
        # first create output directory if necessary
        (directory,namebase)=os.path.split(self.obase)
        fileutils.createdir(directory)        
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
        (sh1r,sh1z,sh1rthresh,sh1zthresh,sh1padj)=seedcorr.calcseedcorr(fileutils.addniigzext(self.splithalfoutputs[0]), \
                                                                        fileutils.addniigzext(self.data.connseed), \
                                                                        self.splithalfoutputs[0], \
                                                                        p_thresh)
        (sh2r,sh2z,sh2rthresh,sh2zthresh,sh2padj)=seedcorr.calcseedcorr(fileutils.addniigzext(self.splithalfoutputs[1]), \
                                                                        fileutils.addniigzext(self.data.connseed), \
                                                                        self.splithalfoutputs[1], \
                                                                        p_thresh)
        
        # split-half reproducibility
        self.splithalfseedconnreproducibility=spmsim.pearsoncorr(sh1r, sh2r)
        # split-half overlap
        self.splithalfseedconnoverlap=spmsim.jaccardind(sh1rthresh, sh2rthresh)
        
    def calcseedconn(self,p_thresh):
        if not self.pipelinerun:
            self.run()
        # do not threshold
        (self.seedconnr,self.seedconnz,self.seedconrthresh,self.seedconnzthresh,padj)=seedcorr.calcseedcorr(fileutils.addniigzext(self.output), fileutils.addniigzext(self.data.connseed),self.output, p_thresh)
        
        self.seedconnrmni152=''
        self.seedconnrthreshmni152=''
        self.seedconnzmni152=''
        self.seedconnzthreshmni152=''
        
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
        
    def seedconn2mni(self):
        if self.seedconnr=='' or self.seedconnz=='':
            sys.exit('Error in seedconn2mni: Seed connectivity not computed. Need to call calcseedconn first')
        # first get transformation parameters on the output of the pipeline
        steps=[preprocessingstep.PreprocessingStep('tmean',[]),\
               preprocessingstep.PreprocessingStep('tomni152',[])]
        #steps=[preprocessingstep.PreprocessingStep('tomni152',[])]
        p=Pipeline('',steps)
        p.setenvvars(self.envvars)
        p.setdata(self.data)
        p.setibase(self.output)
        p.setobase(fileutils.removext(self.output))
        p.run()

        # then use the parameters to transform the SPMs
        p=subprocess.Popen(['flirt','-in',self.seedconnz,\
                            '-ref',self.envvars.mni152,\
                            '-applyxfm','-init',self.data.tomni152,\
                            '-out',fileutils.removext(self.seedconnz)+'_mni152'])
        p.communicate()
        self.seedconnzmni152=fileutils.removext(self.seedconnz)+'_mni152.nii.gz'
        # then the thresholded SPM
        p=subprocess.Popen(['flirt','-in',self.seedconnzthresh,\
                            '-ref',self.envvars.mni152,\
                            '-applyxfm','-init',self.data.tomni152,\
                            '-out',fileutils.removext(self.seedconnzthresh)+'_mni152'])
        p.communicate()
        self.seedconnzthreshmni152=fileutils.removext(self.seedconnzthresh)+'_mni152.nii.gz'

    def output2structural(self):
        if self.data.structural == '':
            sys.exit('In output2structural: Structural data not given. Cannot proceed without. Exiting!')
        p=subprocess.Popen(['flirt','-in',self.output,\
                            '-ref',self.data.structural,\
                            '-out',fileutils.removext(self.output)+'_func2struct',\
                            '-omat',fileutils.removext(self.output)+'_func2struct.mat']) 
        p.communicate()
        p=subprocess.Popen(['convert_xfm','-inverse','-omat',fileutils.removext(self.output)+'_struct2func.mat',\
                            fileutils.removext(self.output)+'_func2struct.mat'])
        p.communicate()
        self.data.func2struct=fileutils.removext(self.output)+'_func2struct.mat'
        self.data.struct2func=fileutils.removext(self.output)+'_struct2func.mat'        

    def parcellate(self):
        if not self.pipelinerun:
            self.run()
        if self.data.structuralcsf=='' or self.data.structuralgm=='' or self.data.structuralwm=='':
            self.data.parcellate_structural()
        if self.data.struct2func=='':
            self.output2structural()
        
        p=subprocess.Popen(['flirt','-in',self.data.structuralcsf,\
                            '-ref',self.output,\
                            '-applyxfm','-init',self.data.struct2func,\
                            '-out',fileutils.removext(self.output)+'_csf'])
        p.communicate()
        p=subprocess.Popen(['fslmaths',fileutils.removext(self.output)+'_csf','-thr','0.5','-bin',fileutils.removext(self.output)+'_csf'])
        p.communicate()
        
        p=subprocess.Popen(['flirt','-in',self.data.structuralgm,\
                            '-ref',self.output,\
                            '-applyxfm','-init',self.data.struct2func,\
                            '-out',fileutils.removext(self.output)+'_gm'])
        p.communicate()
        p=subprocess.Popen(['fslmaths',fileutils.removext(self.output)+'_gm','-thr','0.5','-bin',fileutils.removext(self.output)+'_gm'])
        p.communicate()
        
        p=subprocess.Popen(['flirt','-in',self.data.structuralwm,\
                            '-ref',self.output,\
                            '-applyxfm','-init',self.data.struct2func,\
                            '-out',fileutils.removext(self.output)+'_wm'])
        p.communicate()         
        p=subprocess.Popen(['fslmaths',fileutils.removext(self.output)+'_wm','-thr','0.5','-bin',fileutils.removext(self.output)+'_wm'])
        p.communicate()
        
        self.data.boldcsf=fileutils.removext(self.output)+'_csf.nii.gz'
        self.data.boldgm=fileutils.removext(self.output)+'_gm.nii.gz'
        self.data.boldwm=fileutils.removext(self.output)+'_wm.nii.gz'        
        
        '''
        p=subprocess.Popen(['flirt','-in',self.data.structuralcsfpve,\
                            '-ref',self.output,\
                            '-applyxfm','-init',self.data.struct2func,\
                            '-out',fileutils.removext(self.output)+'_pve_csf'])
        p.communicate()           
        p=subprocess.Popen(['flirt','-in',self.data.structuralgmpve,\
                            '-ref',self.output,\
                            '-applyxfm','-init',self.data.struct2func,\
                            '-out',fileutils.removext(self.output)+'_pve_gm'])
        p.communicate() 
        p=subprocess.Popen(['flirt','-in',self.data.structuralwmpve,\
                            '-ref',self.output,\
                            '-applyxfm','-init',self.data.struct2func,\
                            '-out',fileutils.removext(self.output)+'_pve_wm'])
        p.communicate()        
        
        self.data.boldcsfpve=fileutils.removext(self.output)+'_pve_csf.nii.gz'
        self.data.boldgmpve=fileutils.removext(self.output)+'_pve_gm.nii.gz'
        self.data.boldwmpve=fileutils.removext(self.output)+'_pve_wm.nii.gz'
        
        # threshold
        p=subprocess.Popen(['fslmaths',self.data.boldcsfpve,'-thr','0.7',fileutils.removext(self.output)+'_pve_csf_thr.nii.gz'])
        p.communicate()
        p=subprocess.Popen(['fslmaths',self.data.boldgmpve,'-thr','0.7',fileutils.removext(self.output)+'_pve_gm_thr.nii.gz'])
        p.communicate()
        p=subprocess.Popen(['fslmaths',self.data.boldwmpve,'-thr','0.9',fileutils.removext(self.output)+'_pve_wm_thr.nii.gz'])
        p.communicate()
        
        self.data.boldcsf=fileutils.removext(self.output)+'_pve_csf_thr.nii.gz'
        self.data.boldgm=fileutils.removext(self.output)+'_pve_gm_thr.nii.gz'
        self.data.boldwm=fileutils.removext(self.output)+'_pve_wm_thr.nii.gz'
        '''
        self.parcellated=True
        
        
    def meants(self):
        if self.data.boldcsf=='' or self.data.boldgm=='' or self.data.boldwm=='':
            self.parcellate()
        # compute meant time series for the pipeline output
        p=subprocess.Popen(['fslmeants','-i',self.output,\
                            '-o',fileutils.removext(self.output)+'_meants_csf.txt',\
                            '-m',self.data.boldcsf])
        p.communicate()
        p=subprocess.Popen(['fslmeants','-i',self.output,\
                            '-o',fileutils.removext(self.output)+'_meants_gm.txt',\
                            '-m',self.data.boldgm])
        p.communicate()
        p=subprocess.Popen(['fslmeants','-i',self.output,\
                            '-o',fileutils.removext(self.output)+'_meants_wm.txt',\
                            '-m',self.data.boldwm])
        p.communicate()        

        self.data.meantscsf=fileutils.removext(self.output)+'_meants_csf.txt'
        self.data.meantsgm=fileutils.removext(self.output)+'_meants_gm.txt'
        self.data.meantswm=fileutils.removext(self.output)+'_meants_wm.txt'         
        
        # while here, also compute meant time series for the pipeline input
        p=subprocess.Popen(['fslmeants','-i',self.ibase,\
                            '-o',fileutils.removext(self.ibase)+'_meants_csf.txt',\
                            '-m',self.data.boldcsf])
        p.communicate()
        p=subprocess.Popen(['fslmeants','-i',self.ibase,\
                            '-o',fileutils.removext(self.ibase)+'_meants_gm.txt',\
                            '-m',self.data.boldgm])
        p.communicate()
        p=subprocess.Popen(['fslmeants','-i',self.ibase,\
                            '-o',fileutils.removext(self.ibase)+'_meants_wm.txt',\
                            '-m',self.data.boldwm])
        p.communicate()        

        self.data.imeantscsf=fileutils.removext(self.ibase)+'_meants_csf.txt'
        self.data.imeantsgm=fileutils.removext(self.ibase)+'_meants_gm.txt'
        self.data.imeantswm=fileutils.removext(self.ibase)+'_meants_wm.txt'        
        
        if len(self.seedconnzthresh)>0:
            #fslmeants computes mean over pixels>0 on the mask, so first take abs
            p=subprocess.Popen(['fslmaths',self.output,'-abs',fileutils.removext(self.seedconnzthresh)+'___'])
            p.communicate()
            p=subprocess.Popen(['fslmeants','-i',self.output,\
                                '-o',fileutils.removext(self.output)+'_meants_net.txt',\
                                '-m',fileutils.removext(self.seedconnzthresh)+'___'])
            p.communicate()
            

            p=subprocess.Popen(['fslmeants','-i',self.ibase,\
                                '-o',fileutils.removext(self.ibase)+'_meants_net.txt',\
                                '-m',fileutils.removext(self.seedconnzthresh)+'___'])
            p.communicate()            
            # remove the temp abs mask
            os.remove(fileutils.removext(self.seedconnzthresh)+'___.nii.gz')
            
            self.data.meantsnet=fileutils.removext(self.output)+'_meants_net.txt'
            self.data.imeantsnet=fileutils.removext(self.ibase)+'_meants_net.txt'
            
        self.meantscomputed=True