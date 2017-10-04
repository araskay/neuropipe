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
        self.splithalfseedconnoverlap=None
        #self.connectivityseedfile=''
        self.seedconnoutput=''
        self.seedconn_threshoutput=''
        self.seedconnoutputmni152=''
        self.seedconn_threshoutputmni152=''
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
        ## split-half overlap
        # compute THRESHOLDED seed connectivity maps for each split half
        seedcorr.calcseedcorr(fileutils.addniigzext(self.splithalfoutputs[0]), \
                              fileutils.addniigzext(self.data.connseed), \
                              self.splithalfoutputs[0]+'_seedconn_thr.nii.gz', \
                              0.05) # p_thresh = 0.05
        seedcorr.calcseedcorr(fileutils.addniigzext(self.splithalfoutputs[1]), \
                              fileutils.addniigzext(self.data.connseed), \
                              self.splithalfoutputs[1]+'_seedconn_thr.nii.gz', \
                              0.05) # p_thresh = 0.05       
        self.splithalfseedconnoverlap=spmsim.jaccardind(self.splithalfoutputs[0]+'_seedconn_thr_pearsonr.nii.gz', \
                                                                 self.splithalfoutputs[1]+'_seedconn_thr_pearsonr.nii.gz')
    def calcseedconn(self,p_thresh):
        if not self.pipelinerun:
            self.run()
        # do not threshold
        seedcorr.calcseedcorr(fileutils.addniigzext(self.output), \
                              fileutils.addniigzext(self.data.connseed), \
                              self.output+'_seedconn', \
                              1)
        self.seedconnoutput=self.output+'_seedconn_pearsonr'
        
        # threshold at p_thresh
        seedcorr.calcseedcorr(fileutils.addniigzext(self.output), \
                              fileutils.addniigzext(self.data.connseed), \
                              self.output+'_seedconn_thresh', \
                              p_thresh)
        self.seedconn_threshoutput=self.output+'_seedconn_thresh_pearsonr'
        self.seedconnoutputmni152=''
        self.seedconn_threshoutputmni152=''
        
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
        if self.seedconnoutput=='' or self.seedconn_threshoutput=='':
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
        # then use the parameters to transform the SPM
        # first the unthresholded SPM
        p=subprocess.Popen(['flirt','-in',self.seedconnoutput,\
                            '-ref',self.envvars.mni152,\
                            '-applyxfm','-init',self.data.tomni152,\
                            '-out',fileutils.removext(self.seedconnoutput)+'_2mni152'])
        p.communicate()        
        self.seedconnoutputmni152=fileutils.removext(self.seedconnoutput)+'_2mni152.nii.gz'
        # then the thresholded SPM
        p=subprocess.Popen(['flirt','-in',self.seedconn_threshoutput,\
                            '-ref',self.envvars.mni152,\
                            '-applyxfm','-init',self.data.tomni152,\
                            '-out',fileutils.removext(self.seedconn_threshoutput)+'_2mni152'])
        p.communicate()
        self.seedconn_threshoutputmni152=fileutils.removext(self.seedconn_threshoutput)+'_2mni152.nii.gz'

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
        if self.data.structuralcsfseg=='' or self.data.structuralgmseg=='' or self.data.structuralwmseg=='':
            self.data.parcellate_mprage()
        if self.data.struct2func=='':
            self.output2structural()
        
        p=subprocess.Popen(['flirt','-in',self.data.structuralcsfseg,\
                            '-ref',self.output,\
                            '-applyxfm','-init',self.data.struct2func,\
                            '-out',fileutils.removext(self.output)+'_seg_csf'])
        p.communicate()           
        p=subprocess.Popen(['flirt','-in',self.data.structuralgmseg,\
                            '-ref',self.output,\
                            '-applyxfm','-init',self.data.struct2func,\
                            '-out',fileutils.removext(self.output)+'_seg_gm'])
        p.communicate() 
        p=subprocess.Popen(['flirt','-in',self.data.structuralwmseg,\
                            '-ref',self.output,\
                            '-applyxfm','-init',self.data.struct2func,\
                            '-out',fileutils.removext(self.output)+'_seg_wm'])
        p.communicate()         

        self.data.boldcsfseg=fileutils.removext(self.output)+'_seg_csf.nii.gz'
        self.data.boldgmseg=fileutils.removext(self.output)+'_seg_gm.nii.gz'
        self.data.boldwmseg=fileutils.removext(self.output)+'_seg_wm.nii.gz'        
        
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
        
        if len(self.seedconn_threshoutput)>0:
            p=subprocess.Popen(['fslmeants','-i',self.output,\
                                '-o',fileutils.removext(self.output)+'_meants_net.txt',\
                                '-m',self.seedconn_threshoutput])
            p.communicate()             

            p=subprocess.Popen(['fslmeants','-i',self.ibase,\
                                '-o',fileutils.removext(self.ibase)+'_meants_net.txt',\
                                '-m',self.seedconn_threshoutput])
            p.communicate()            
            
            self.data.meantsnet=fileutils.removext(self.output)+'_meants_net.txt'
            self.data.imeantsnet=fileutils.removext(self.ibase)+'_meants_net.txt'
            
        self.meantscomputed=True