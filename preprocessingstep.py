# Library including the definition of the class PreprocessingStep and its routines.
# Also includes functions related to making lists of steps from a text pipeline file
# and various permutations.
# Add any new preprocessing step here under the run() subroutine.
# Report bugs/issues to M. Aras Kayvanrad (mkayvan@gmail.com).
# (c) M. Aras Kayvanrad

import subprocess # used to run bash commands
import sys
import os
import fileutils
import nibabel
from nipype.algorithms.confounds import (ACompCor, TCompCor)
import shutil
import numpy as np
import scipy
import scipy.signal
import copy

class PreprocessingStep:
    def __init__(self,name,params):
        self.name=name
        self.params=params
        self.ibase=''
        self.obase=''
        self.data=None
        
    def setibase(self,ibase):
        self.ibase=ibase
        
    def setobase(self,obase):
        self.obase=obase
    
    def setdata(self,data):
        self.data=data
        
                
    def run(self):
        ## fsl mcflirt
        if (self.name == 'mcflirt'):
            process=subprocess.Popen(['mcflirt','-in',self.ibase,'-out',self.obase,'-plots'])
            (output,error)=process.communicate()
            self.data.motpar=fileutils.removeniftiext(self.obase)+'.par'
        
        ## afni spatial smoothing
        elif (self.name == 'ssmooth'):
            if '-fwhm' in self.params:
                fwhm=str(self.params[self.params.index('-fwhm')+1])
            else:
                fwhm='5' #default
            process=subprocess.Popen(['3dmerge', \
                                      '-prefix', fileutils.removeniftiext(self.obase), '-overwrite',\
                                      '-doall', \
                                      '-quiet', \
                                      '-1blur_fwhm', fwhm, \
                                      fileutils.addniigzext(self.ibase)])
            (output,error)=process.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase))
            # if brain extraction was already performed, reapply the brain mask
            if self.data.brainmask != '':
                p=subprocess.Popen(['fslmaths',self.obase,'-mas',self.data.brainmask,self.obase])
                p.communicate()
          
        ## motcor (motion correction with a PCA-based min. displacement reference)
        elif (self.name == 'motcor'):
            # I. estimate min. displacement brain volume
            # first obtain a brain mask
            process=subprocess.Popen(['3dAutomask', '-q', \
                                      '-prefix',fileutils.removeniftiext(self.obase)+'_temp_brainmask', \
                                      fileutils.addniigzext(self.ibase)])
            (output,error)=process.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase)+'_temp_brainmask')
            # now find min. displacement brain volume
            process=subprocess.Popen(['matlab', \
                                      '-nodisplay','-nosplash', \
                                      '-r', 'min_displace_brick('+ \
                                      '\''+fileutils.addniigzext(self.ibase)+'\',' + \
                                      '\''+fileutils.removeniftiext(self.obase)+'_temp_brainmask.nii.gz'+'\',' + \
                                      '\''+fileutils.removeniftiext(self.obase)+'_temp_mindisplacementInd'+'\'); '+ \
                                      'quit;'])
            (output,error)=process.communicate()
            # now coregister all volumes to the reference found above
            f=open(fileutils.removeniftiext(self.obase)+'_temp_mindisplacementInd_0ref_motbrick.txt','r')
            # matlab scripts adds the _0ref_motbrick.txt part to the file name
            ind=f.read();
            ind=ind[0:-1] # remove \n
            f.close()
            process=subprocess.Popen(['3dvolreg', \
                                      '-prefix', fileutils.removeniftiext(self.obase), \
                                      '-base', ind, \
                                      fileutils.addniigzext(self.ibase)])
            (output,error)=process.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase))
            fileutils.removefile(fileutils.removeniftiext(self.obase)+'_temp_brainmask.nii.gz')
            fileutils.removefile(fileutils.removeniftiext(self.obase)+'_temp_mindisplacementInd_0ref_motbrick.txt')
            
        elif (self.name == 'retroicor'):
            physparams=[]
            otherparams=[]
            if self.data.card != '':
                physparams.append('-card')
                physparams.append(self.data.card)
            if self.data.resp != '':
                physparams.append('-resp')
                physparams.append(self.data.resp)
            if '-ignore' in self.params:
                otherparams.append('-ignore')
                otherparams.append(self.params[self.params.index('-ignore')+1])
            if '-threshold' in self.params:
                otherparams.append('-threshold')
                otherparams.append(self.params[self.params.index('-threshold')+1])
            if '-order' in self.params:
                otherparams.append('-order')
                otherparams.append(self.params[self.params.index('-order')+1])
            if '-cardphase' in self.params:
                otherparams.append('-cardphase')
                otherparams.append(fileutils.removext(self.obase)+'_cardphase.txt')
                self.data.cardphase = fileutils.removext(self.obase)+'_cardphase.txt'
            if '-respphase' in self.params:
                otherparams.append('-respphase')
                otherparams.append(fileutils.removext(self.obase)+'_respphase.txt')
                self.data.respphase = fileutils.removext(self.obase)+'_respphase.txt'
            
            process=subprocess.Popen(['3dretroicor', '-prefix', fileutils.removext(self.obase),'-overwrite']+ \
                                     physparams + otherparams + \
                                     [fileutils.addniigzext(self.ibase)])
            (output,error)=process.communicate()
            fileutils.afni2nifti(fileutils.removext(self.obase))           
        
        elif (self.name == '3dSkullStrip'):
            process=subprocess.Popen(['3dSkullStrip',\
                                      '-input',fileutils.addniigzext(self.ibase),\
                                      '-prefix', fileutils.removeniftiext(self.obase),'-overwrite'])
            process.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase))
        
        elif (self.name == 'bet'):
            p=subprocess.Popen(['bet',self.ibase,self.obase]+self.params)
            p.communicate()

        elif (self.name == 'fslreorient2std'):
            p=subprocess.Popen(['fslreorient2std',self.ibase,self.obase])
            p.communicate()
            
        elif (self.name == 'brainExtractAFNI'):
            # first use 3dAutomask to create a brain mask
            process=subprocess.Popen(['3dAutomask', '-q', \
                                      '-prefix',fileutils.removeniftiext(self.obase)+'__brainmask','-overwrite', \
                                      fileutils.addniigzext(self.ibase)])
            (output,error)=process.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase)+'__brainmask')
            # then use the mask to extract the 4D functional data
            p=subprocess.Popen(['fslmaths',self.ibase,\
                                '-mas',fileutils.removeniftiext(self.obase)+'__brainmask',\
                                fileutils.removeniftiext(self.obase)])
            p.communicate()
            self.data.brainmask = fileutils.removeniftiext(self.obase)+'__brainmask.nii.gz'

        elif (self.name == 'brainExtractFSL'):
            # first extract brain mask from a temporal mean volume
            p=subprocess.Popen(['fslmaths',self.ibase,'-Tmean',fileutils.removeniftiext(self.obase)+'__tmean'])
            p.communicate()
            p=subprocess.Popen(['bet2',fileutils.removeniftiext(self.obase)+'__tmean',\
                                fileutils.removeniftiext(self.obase)+'__tmean',\
                                '-f','0.3','-n','-m']) # create a binary mask from the the mean image. (bet2 automatically adds a _mask suffix to the output file)
            p.communicate()
            # then use the mask to extract the 4D functional data
            p=subprocess.Popen(['fslmaths',self.ibase,\
                                '-mas',fileutils.removeniftiext(self.obase)+'__tmean_mask',\
                                self.obase])
            p.communicate()
            fileutils.removefile(fileutils.removeniftiext(self.obase)+'__tmean.nii.gz')
            self.data.brainmask=fileutils.removeniftiext(self.obase)+'__tmean_mask.nii.gz'
            
        elif (self.name == '3dFourier'):
            p=subprocess.Popen(['3dFourier']+self.params+\
                               ['-prefix',fileutils.removeniftiext(self.obase),fileutils.addniigzext(self.ibase)])
            p.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase))                         
         
        elif (self.name == 'motreg'):
            if self.data.motpar=='':
                sys.exit('Cannot run regmot- no motion parameters available. Need to either provide motion parameters or have mcflirt run before regmot')
            # convert motion parameters to design matrix
            # (this is not required- fsl_glm works the same without coversion using Text2Vest)
            p=subprocess.Popen(['Text2Vest',self.data.motpar,fileutils.removext(self.data.motpar)+'.mat'])
            p.communicate()
            
            if self.data.brainmask=='':
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',fileutils.removext(self.data.motpar)+'.mat',\
                                    '-o',fileutils.removeniftiext(self.obase)+'__motglm',\
                                    '--out_res='+self.obase])
            else:
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',fileutils.removext(self.data.motpar)+'.mat',\
                                    '-m',self.data.brainmask,\
                                    '-o',fileutils.removeniftiext(self.obase)+'__motglm',\
                                    '--out_res='+self.obase])
                
            p.communicate()
            self.data.glm=fileutils.removeniftiext(self.obase)+'__motglm'
        
        elif self.name=='slicetimer':
            # get the TR from the data
            img_nib=nibabel.load(fileutils.addniigzext(self.ibase))
            hdr=img_nib.header
            tr=str(hdr.get_zooms()[3])
            if 'interleaved' in self.data.slicetiming.lower():
                if not '--odd' in self.params:
                    self.params.append('--odd')
            if ('descending' in self.data.slicetiming.lower() or
                    'reverse' in self.data.slicetiming.lower()):
                if not '--down' in self.params:
                    self.params.append('--down')
                
            p=subprocess.Popen(['slicetimer','-i',self.ibase,'-o',self.obase,'-r',tr]+self.params)
            p.communicate()                


        elif self.name=='stcor':
            # get the TR from the data
            img_nib=nibabel.load(fileutils.addniigzext(self.ibase))
            hdr=img_nib.header
            tr=str(hdr.get_zooms()[3]*1000)
            if len(self.data.slicetiming)>0:
                p=subprocess.Popen(['3dTshift','-TR',tr,'-tpattern','@'+self.data.slicetiming,\
                                    '-prefix',fileutils.removext(self.obase), '-overwrite', fileutils.addniigzext(self.ibase)])
                p.communicate()
                fileutils.afni2nifti(fileutils.removeniftiext(self.obase))
            else:
                sys.exit('Please provide slice timing offsets for slice timing correction.')                
                
        elif self.name=='phycaa':
            # get the TR from the data
            img_nib=nibabel.load(fileutils.addniigzext(self.ibase))
            hdr=img_nib.header
            tr=str(hdr.get_zooms()[3])

            if self.data.brainmask=='':
                sys.exit('Error in phycaa: no brainmask available. Consider adding brainExtractAfni or brainExtractFSL or providing brainmask in the subjects file')
            
            # need to change NIFTI_GZ to NIFTI (aparently phycaa cannot handle nifti_gz)
            process=subprocess.Popen(['matlab', \
                                      '-nodisplay','-nosplash', \
                                      '-r', 'run_phycaa('+ \
                                      '\''+fileutils.unzipnifti(self.ibase)+'\',' + \
                                      '\''+fileutils.unzipnifti(self.data.brainmask)+'\',' + \
                                      tr+ \
                                      ',\''+fileutils.removext(self.obase)+'\'); '+ \
                                      'quit;'])
            (output,error)=process.communicate()
            print('PHYCAA+ done.')

            # remove unzipped nifti files
            fileutils.removefile(fileutils.removext(self.ibase)+'.nii')
            fileutils.removefile(fileutils.removext(self.data.brainmask)+'.nii')
            # move phycaa main output to self.obase
            shutil.move(fileutils.removext(self.ibase)+'_PHYCAA_step1+2.nii',fileutils.removext(self.obase)+'.nii')
            # zip phycaa output to produce nii.gz file
            fileutils.zipnifti(fileutils.removext(self.obase))
            # save the regressors in the data
            self.data.phycaCompS1 = fileutils.removext(self.obase)+'_noisecomp_split1.csv'
            self.data.phycaCompS2 = fileutils.removext(self.obase)+'_noisecomp_split2.csv'
        
        elif self.name=='tcompcor':
            if '-ignore' in self.params:
                ignore=int(self.params[self.params.index('-ignore')+1])
            else:
                ignore=0
            ccor = TCompCor()
            ccor.inputs.realigned_file = fileutils.addniigzext(self.ibase)
#            if self.data.brainmask != '':
#                ccor.inputs.mask_files = self.data.brainmask

            ccor.inputs.components_file=fileutils.removext(self.obase)+'__components.txt'
            #ccor.inputs.header_prefix='' # not sure what this does
            ccor.inputs.num_components=6 # based on Behzadi's paper, also nipype default
            ccor.inputs.percentile_threshold=0.02 # based on Behzadi's paper, also nipype default
            ccor.inputs.ignore_initial_volumes=ignore
            ccor.inputs.pre_filter = False # just remove mean, do not do further detrending
            ccor.run()
            # the following commented to run in parallel
            #shutil.move('mask_000.nii.gz',fileutils.removext(self.obase)+'__hivarmask.nii.gz') # cannot set output path for high variance mask
            
            if self.data.brainmask=='':
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',fileutils.removext(self.obase)+'__components.txt',\
                                    '-o',fileutils.removext(self.obase)+'__regmodel',\
                                    '--out_res='+self.obase])
            else:
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',fileutils.removext(self.obase)+'__components.txt',\
                                    '-m',self.data.brainmask,\
                                    '-o',fileutils.removext(self.obase)+'__regmodel',\
                                    '--out_res='+self.obase])
                
            p.communicate()

            self.data.tcompPCs = fileutils.removext(self.obase)+'__components.txt'

        elif self.name=='acompcor':
            if not '-mask' in self.params:
                sys.exit('ERROR in acompcor: need to provide mask for acompcor. Available options are csf, wm, and csfwm.')
            ccor = ACompCor()

            mask=self.params[self.params.index('-mask')+1]
            if mask=='csf':
                if self.data.boldcsf=='':
                    self.data.parcellate_bold()
                ccor.inputs.mask_files=self.data.boldcsf
            elif mask=='wm':
                if self.data.boldwm=='':
                    self.data.parcellate_bold()
                ccor.inputs.mask_files=self.data.boldwm
            elif mask=='csfwm':
                if self.data.boldcsfwm=='':
                    self.data.parcellate_bold()
                ccor.inputs.mask_files=self.data.boldcsfwm
            else:
                sys.exit('ERROR in acompcor: given mask not known. Available options are csf, wm, and csfwm.')

            if '-ignore' in self.params:
                ignore=int(self.params[self.params.index('-ignore')+1])
            else:
                ignore=0
            
            ccor.inputs.realigned_file = fileutils.addniigzext(self.ibase)
#            if self.data.brainmask != '':
#                ccor.inputs.mask_files = self.data.brainmask

            ccor.inputs.components_file=fileutils.removext(self.obase)+'__components.txt'
            #ccor.inputs.header_prefix='' # not sure what this does
            ccor.inputs.num_components=6 # based on Behzadi's paper, also nipype default
            ccor.inputs.ignore_initial_volumes=ignore
            ccor.inputs.pre_filter = False # just remove mean, do not do further detrending
            ccor.run()

            if self.data.brainmask=='':
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',fileutils.removext(self.obase)+'__components.txt',\
                                    '-o',fileutils.removext(self.obase)+'__regmodel',\
                                    '--out_res='+self.obase])
            else:
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',fileutils.removext(self.obase)+'__components.txt',\
                                    '-m',self.data.brainmask,\
                                    '-o',fileutils.removext(self.obase)+'__regmodel',\
                                    '--out_res='+self.obase])
                
            p.communicate()

            self.data.acompPCs = fileutils.removext(self.obase)+'__components.txt'

        elif self.name=='fsl_motion_outliers':
            p=subprocess.Popen(['fsl_motion_outliers','-i',self.ibase,'-o',fileutils.removext(self.obase)+'__confound.txt','-s',fileutils.removext(self.obase)+'__metric.txt']+self.params)
            p.communicate()
            
            self.data.motmetric = fileutils.removext(self.obase)+'__metric.txt'

            # can use with fsl_glm as follows:
            # p=subprocess.Popen(['fsl_glm','-i',self.ibase,'-d',fileutils.removext(self.obase)+'__confound.txt','-o',fileutils.removext(self.obase)+'__regmodel','--out_res='+self.obase,'-m',self.data.brainmask])
            # p.communicate()

            img_nib=nibabel.load(fileutils.addniigzext(self.ibase))
            img=img_nib.get_data()
            hdr=img_nib.header
            affine=img_nib.affine # used to save the result in a NIFTI file
            tr=hdr.get_zooms()[3]

            # interpolate if there are outliers (otherwise no confoud file generated)
            if os.path.exists(fileutils.removext(self.obase)+'__confound.txt'):
                confoundmat=np.loadtxt(fileutils.removext(self.obase)+'__confound.txt')
                # if there is only one corrupt volume, confoundmat will
                # be a vector, otherwise, a matrix - one column for each
                # corrupt volume
                if len(confoundmat.shape) == 1:
                    outlier = confoundmat
                else:
                    outlier=np.sum(confoundmat,axis=1) # a vector in which outlier volumes are indicated by 1 and non-outliers by 0
                
                t=tr*np.arange(0,img.shape[3])

                for x in np.arange(0,img.shape[0]):
                    for y in np.arange(0,img.shape[1]):
                        for z in np.arange(0,img.shape[2]):
                            t_nonoutlier=t[np.where(outlier != 1)]
                            sig_nonoutlier=img[x,y,z,np.where(outlier != 1)]
                            f=scipy.interpolate.interp1d(t_nonoutlier,sig_nonoutlier,fill_value="extrapolate")
                            img[x,y,z,np.where(outlier==1)]=f(t[np.where(outlier==1)])

            onifti = nibabel.nifti1.Nifti1Image(img,affine,header=hdr)
            onifti.to_filename(fileutils.removeniftiext(self.obase)+'.nii.gz')
 
        elif self.name=='lpf':
            img_nib=nibabel.load(fileutils.addniigzext(self.ibase))
            img=img_nib.get_data()
            hdr=img_nib.header
            affine=img_nib.affine # used to save the result in a NIFTI file
            tr=hdr.get_zooms()[3]
            fs=1/tr
            
            Fstop=float(self.params[0])/(fs/2)

            print('LPF:')
            print('TR=',tr)
            print('Nq=',fs/2)
            print('Fstop=',Fstop, '(Normalized Frequency)')
            
            if Fstop>1:
                sys.exit('ERROR in lpf: Cut-off frequency is beyond Nyquist rate.')
            
            (b,a)=scipy.signal.butter(5,Fstop,btype='lowpass')
            
            img = scipy.signal.filtfilt(b,a,img,axis=-1)
            
            # replace the firt time point with temporal mean
            img[:,:,:,0]=np.mean(img,axis=-1)
            
            onifti = nibabel.nifti1.Nifti1Image(img,affine,header=hdr)
            onifti.to_filename(fileutils.removeniftiext(self.obase)+'.nii.gz')            
            
        elif self.name=='hpf':
            img_nib=nibabel.load(fileutils.addniigzext(self.ibase))
            img=img_nib.get_data()
            hdr=img_nib.header
            affine=img_nib.affine # used to save the result in a NIFTI file
            tr=hdr.get_zooms()[3]
            fs=1/tr
            
            Fstop=float(self.params[0])/(fs/2)
            
            print('HPF:')
            print('TR=',tr)
            print('Nq=',fs/2)
            print('Fstop=',Fstop, '(Normalized Frequency)')

            if Fstop>1:
                sys.exit('ERROR in hpf: Cut-off frequency is beyond Nyquist rate.')
            
            (b,a)=scipy.signal.butter(5,Fstop,btype='highpass')
            
            img = scipy.signal.filtfilt(b,a,img,axis=-1)
            
            # replace the firt time point with temporal mean
            img[:,:,:,0]=np.mean(img,axis=-1)
            
            onifti = nibabel.nifti1.Nifti1Image(img,affine,header=hdr)
            onifti.to_filename(fileutils.removeniftiext(self.obase)+'.nii.gz')            
                        
        elif self.name=='bpf':
            img_nib=nibabel.load(fileutils.addniigzext(self.ibase))
            img=img_nib.get_data()
            hdr=img_nib.header
            affine=img_nib.affine # used to save the result in a NIFTI file
            tr=hdr.get_zooms()[3]
            fs=1/tr

            Fstop1=float(self.params[0])/(fs/2)
            Fstop2=float(self.params[1])/(fs/2)

            print('BPF:')
            print('TR=',tr)
            print('Nq=',fs/2)              
            print('Fstop1=',Fstop1, '(Normalized Frequency)')
            print('Fstop2=',Fstop2, '(Normalized Frequency)')
            
            if Fstop1>1 or Fstop2>1:
                sys.exit('ERROR in bpf: Cut-off frequency is beyond Nyquist rate.')

            (b,a)=scipy.signal.butter(5,(Fstop1,Fstop2),btype='bandpass')
            
            img = scipy.signal.filtfilt(b,a,img,axis=-1)
            
            # replace the firt time point with temporal mean
            img[:,:,:,0]=np.mean(img,axis=-1)
            
            onifti = nibabel.nifti1.Nifti1Image(img,affine,header=hdr)
            onifti.to_filename(fileutils.removeniftiext(self.obase)+'.nii.gz')
            
        elif self.name=='globalsigreg':
            if self.data.meants=='':
                if self.data.brainmask=='':
                    sys.exit('ERROR: to run globalsigreg either it must be preceded by brain extraction or meants should be provided in the subjects file.')
                else:
                    data=copy.deepcopy(self.data)
                    data.bold=self.ibase
                    data.calc_meants()
            else:
                data=copy.deepcopy(self.data)
            if self.data.brainmask=='':
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',data.meants,\
                                    '-o',fileutils.removext(self.obase)+'__globalsigglm',\
                                    '--out_res='+self.obase])
            else:
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',data.meants,\
                                    '-m',self.data.brainmask,\
                                    '-o',fileutils.removext(self.obase)+'__globalsigglm',\
                                    '--out_res='+self.obase])                    
            p.communicate()
            self.data.gsr = data.meants            

        elif self.name=='csfreg':
            if self.data.meantscsf=='':
                data=copy.deepcopy(self.data)
                data.bold=self.ibase
                data.calc_meants()
            else:
                data=copy.deepcopy(self.data)
            if self.data.brainmask=='':
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',data.meantscsf,\
                                    '-o',fileutils.removext(self.obase)+'__csfglm',\
                                    '--out_res='+self.obase])
            else:
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',data.meantscsf,\
                                    '-m',self.data.brainmask,\
                                    '-o',fileutils.removext(self.obase)+'__csfglm',\
                                    '--out_res='+self.obase])
        
            p.communicate()
            self.data.csfr = data.meantscsf         
            
        elif self.name=='wmreg':
            if self.data.meantswm=='':
                data=copy.deepcopy(self.data)
                data.bold=self.ibase
                data.calc_meants()
            else:
                data=copy.deepcopy(self.data)
            if self.data.brainmask=='':
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',data.meantswm,\
                                    '-o',fileutils.removext(self.obase)+'__wmglm',\
                                    '--out_res='+self.obase])
            else:
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',data.meantswm,\
                                    '-m',self.data.brainmask,\
                                    '-o',fileutils.removext(self.obase)+'__wmglm',\
                                    '--out_res='+self.obase])                
            p.communicate()
            self.data.wmr = data.meantswm
            
        elif self.name=='csfwmreg':
            if self.data.meantscsfwm=='':
                data=copy.deepcopy(self.data)
                data.bold=self.ibase
                data.calc_meants()
            else:
                data=copy.deepcopy(self.data)
            if self.data.brainmask=='':
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',data.meantscsfwm,\
                                    '-o',fileutils.removext(self.obase)+'__csfwmglm',\
                                    '--out_res='+self.obase])
            else:
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',data.meantscsfwm,\
                                    '-m',self.data.brainmask,\
                                    '-o',fileutils.removext(self.obase)+'__csfwmglm',\
                                    '--out_res='+self.obase])                
            p.communicate()
            self.data.csfwmr = data.meantscsfwm          

        elif (self.name == '3dDetrend'):
            p=subprocess.Popen(['3dDetrend']+self.params+\
                               ['-prefix',fileutils.removeniftiext(self.obase),\
                                fileutils.addniigzext(self.ibase)])
            p.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase)) 
            
        elif (self.name == 'remove_spatial_structure_3dDeconvolve'):
            p=subprocess.Popen(['3dDeconvolve']+self.params+\
                               ['-input',fileutils.addniigzext(self.ibase),\
                                '-prefix',fileutils.removeniftiext(self.obase)+'_3dDecon',\
                                '-errts',fileutils.removeniftiext(self.obase)])
            p.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase)) 
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase)+'_3dDecon')

        elif (self.name == '3dBlurToFWHM'):
            p=subprocess.Popen(['3dBlurToFWHM']+self.params+\
                               ['-prefix',fileutils.removeniftiext(self.obase),\
                                '-input',fileutils.addniigzext(self.ibase)])
            p.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase)) 

        elif self.name=='spikecor':
            # get OUT_PARAM
            out_param='volume' # default
            if '-out_param' in self.params:
                out_param = self.params[self.params.index('-out_param')+1]
           
            if not out_param in ['none','motion','volume','volume+motion','slice','slice+motion']:
                    sys.exit('Error: spikecor interpolation parameter (OUT_PARAM) is not valid. OUT_PARAM can be one of the followin: none, motion, volume, volume+motion, slice, slice+motion.')

            print('Spikecor: out_param set to '+out_param)

            
            if self.data.brainmask=='':
                print('Warning in spikecor: no brainmask available. Using the entire image as mask.')
            
            if self.data.motpar=='':
                print('Warning in SpikeCor: motion parameters not available. Assuming zero motion.')
                
            # need to change NIFTI_GZ to NIFTI (aparently spikecore cannot handle nifti_gz)
            process=subprocess.Popen(['matlab', \
                                      '-nodisplay','-nosplash', \
                                      '-r', 'run_spikecor('+ \
                                      '\''+fileutils.unzipnifti(self.ibase)+'\',' + \
                                      '\''+fileutils.unzipnifti(self.data.brainmask)+'\',' + \
                                      '\''+self.data.motpar+'\',' + \
                                      '\''+fileutils.removext(self.obase)+'\','+ \
                                      '\''+out_param+'\',' + \
                                      '\''+fileutils.removext(self.obase)+'.nii\'); '+ \
                                      'quit;'])
            (output,error)=process.communicate()
            print('SpikeCor done.')

            # remove unzipped nifti files
            fileutils.removefile(fileutils.removext(self.ibase)+'.nii')
            fileutils.removefile(fileutils.removext(self.data.brainmask)+'.nii')
            # zip output to produce nii.gz file
            fileutils.zipnifti(fileutils.removext(self.obase))
            
        elif self.name=='regress-out':
            # check if at least one regressor given
            if len(self.params)==0:
                sys.exit('ERROR in preprocessing step regress-out: please specify at least one regressor.')
            # check if all the given regressors are valid
            valid=['motpar','motpar_derivatives']
            invalid=False
            for r in self.params:
                if not r in valid:
                    invalid = True
            if invalid:
                sys.exit('ERROR in preprocessing step regress-out: one or more invalid regressor(s) given.')
                
            rmat = np.array([])
            regressors = ''
            if 'motpar' in self.params:
                if self.data.motpar=='':
                    sys.exit('ERROR in preprocessing step regress-out: requested to regress-out motion parameters but no motion parameters available. Need to either provide motion parameters or have mcflirt run before this step.')
                r = np.loadtxt(self.data.motpar)
                rmat = np.concatenate((rmat,r),axis=1) if rmat.size else r
                regressors += '_motpar'
            if 'motpar_derivatives' in self.params:
                if self.data.motpar=='':
                    sys.exit('ERROR in preprocessing step regress-out: requested to regress-out motion parameters derivatives but no motion parameters available. Need to either provide motion parameters or have mcflirt run before this step.')
                motpar = np.loadtxt(self.data.motpar)
                motpar_shift = np.roll(motpar,-1,axis=0)
                r = np.zeros(motpar.shape)
                r[0:-1,] = motpar_shift[0:-1,]-motpar[0:-1,]
                # replace the last row (which is zero) with the previous one
                r[-1,] = r[-2,]
                rmat = np.concatenate((rmat,r),axis=1) if rmat.size else r
                regressors += '_motpar_derivatives'
                
            np.savetxt(fileutils.removext(self.obase)+regressors+'_regressors.txt',rmat)
            
            # convert regressors to design matrix
            # (this is not required- fsl_glm works the same without coversion using Text2Vest)
            p=subprocess.Popen(['Text2Vest',fileutils.removext(self.obase)+regressors+'_regressors.txt',fileutils.removext(self.obase)+regressors+'_regressors.mat'])
            p.communicate()            
            
            if self.data.brainmask=='':
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',fileutils.removext(self.obase)+regressors+'_regressors.mat',\
                                    '-o',fileutils.removeniftiext(self.obase)+'__glm',\
                                    '--out_res='+self.obase])
            else:
                p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                    '-d',fileutils.removext(self.obase)+regressors+'_regressors.mat',\
                                    '-m',self.data.brainmask,\
                                    '-o',fileutils.removeniftiext(self.obase)+'__glm',\
                                    '--out_res='+self.obase])
                
            p.communicate()            
            self.data.glm=fileutils.removeniftiext(self.obase)+'__glm'            

        else:
            sys.exit('Error: preprocessing step '+self.name+' not defined')      
    
    # remove output files (for intermediate steps, if keepintermed = False)
    def removeofiles(self):
        if (self.name == 'mcflirt'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'ssmooth'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'motcor'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'retroicor'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == '3dSkullStrip'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'bet'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'fslreorient2std'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'brainExtractAFNI'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'brainExtractFSL'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == '3dFourier'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'motreg'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'slicetimer'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'stcor'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'phycaa'):
            fileutils.removefile(fileutils.addniigzext(self.obase))            
        elif (self.name == 'tcompcor'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'acompcor'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'fsl_motion_outliers'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'lpf'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'hpf'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'bpf'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'globalsigreg'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'csfreg'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'wmreg'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'csfwmreg'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == '3dDetrend'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'remove_spatial_structure_3dDeconvolve'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
            # there are other files though, which can also be removed.
        elif (self.name == '3dBlurToFWHM'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'spikecor'):
            fileutils.removefile(fileutils.addniigzext(self.obase))
        elif (self.name == 'regress-out'):
            fileutils.removefile(fileutils.addniigzext(self.obase))            
        else:
            sys.exit('Error: preprocessing step '+self.name+' not defined')    

# read the text pipeline file and create a list of the steps
def makesteps(pipelinefile):
    steps=[]
    f=open(pipelinefile)
    line=f.readline()
    s=line.split()
    while len(s)>0:
        name=s[0]
        params=s[1:]
        step=PreprocessingStep(name,params)
        steps.append(step)
        line=f.readline()
        s=line.split()
    return(steps)

# generate all the permutations of the elements of the input list
def permutations(l):
    if len(l)==0:
        yield([])    
    elif len(l) == 1:
        yield(l)
    elif len(l)>1:
        for p in permutations(l[1:]):
            for i in range(len(l)):
                yield(p[:i]+l[0:1]+p[i:])

# generate all the on/off combinations of the elements of the input list,
# retaining the original order
def onoff(l):
    if len(l)==0:
        yield([])
    elif len(l) == 1:
        yield(l)
        yield([])
    elif len(l)>1:
        for p in onoff(l[1:]):
            yield(l[0:1]+p)
            yield(p)

# generate all the permutations from all the on/off combinations
# i.e., combine permutations and onoff functions
def permonoff(l):
    for p in onoff(l):
        for q in permutations(p):
            yield(q)

# select one element from the input list at a time, and return that element
# used to generate combinations by selecting from a list of steps 
def select(l):
    for p in l:
        yield([p])
    
def concatstepslists(l1,l2):
    # NOTE: inputs must be lists of lists NOT generators
    if len(l1)==0 and len(l2)>0:
        for p in l2:
            yield(p)
    elif len(l1)>0 and len(l2)==0:
        for p in l1:
            yield(p)
    elif len(l1)>0 and len(l2)>0:
        for p1 in l1:
            for p2 in l2:
                yield(p1+p2)

