import subprocess # used to run bash commands
import sys
import seedcorr
import fileutils
import os

class PreprocessingStep:
    def __init__(self,name,params):
        self.name=name
        self.params=params
        
    def setibase(self,ibase):
        self.ibase=ibase
        
    def setobase(self,obase):
        self.obase=obase
                
    def run(self):
        ## fsl mcflirt
        if (self.name == 'mcflirt'):
            process=subprocess.Popen(['mcflirt','-in',self.ibase,'-out',self.obase,'-plots'])
            (output,error)=process.communicate()
        
        ## seed connectivity
        elif (self.name == 'seedconn'):
            seedcorr.calcseedcorr(fileutils.addniigzext(self.ibase), \
                                  self.params[self.params.index('-seed')+1], \
                                  fileutils.addniigzext(self.obase), \
                                  float(self.params[self.params.index('-spm_thresh')+1])) 
        
        ## afni spatial smoothing
        elif (self.name == 'ssmooth'):
            process=subprocess.Popen(['3dmerge', \
                                      '-prefix', fileutils.removeniftiext(self.obase), \
                                      '-doall', \
                                      '-quiet', \
                                      '-1blur_fwhm', str(self.params[self.params.index('-fwhm')+1]), \
                                      fileutils.addniigzext(self.ibase)])
            (output,error)=process.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase))
          
        ## motcor (motion correction with a PCA-based min. displacement reference)
        elif (self.name == 'motcor'):
            # I. estimate min. displacement brain volume
            # first obtain a brain mask
            process=subprocess.Popen(['3dAutomask', \
                                      '-prefix',fileutils.removeniftiext(self.obase)+'_brainmask', \
                                      fileutils.addniigzext(self.ibase)])
            (output,error)=process.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase)+'_brainmask')
            # now find min. displacement brain volume
            process=subprocess.Popen(['matlab', \
                                      '-nodisplay','-nosplash', \
                                      '-r', 'min_displace_brick('+ \
                                      '\''+fileutils.addniigzext(self.ibase)+'\',' + \
                                      '\''+fileutils.removeniftiext(self.obase)+'_brainmask.nii.gz'+'\',' + \
                                      '\''+fileutils.removeniftiext(self.obase)+'_mindisplacementInd'+'\'); '+ \
                                      'quit;'])
            (output,error)=process.communicate()
            # now coregister all volumes to the reference found above
            f=open(fileutils.removeniftiext(self.obase)+'_mindisplacementInd_0ref_motbrick.txt','r')
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
            
        elif (self.name == 'retroicor'):
            process=subprocess.Popen(['3dretroicor', \
                                      '-prefix', fileutils.removeniftiext(self.obase), \
                                      '-ignore', self.params[self.params.index('-ignore')+1], \
                                      '-card', self.params[self.params.index('-card')+1], \
                                      '-resp', self.params[self.params.index('-resp')+1], \
                                      fileutils.addniigzext(self.ibase)])
            (output,error)=process.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase))           
        
        else:
            sys.exit('Error: preprocessing step not defined')
            
    def removeofiles(self):
        if (self.name == 'mcflirt'):
            os.remove(fileutils.removeniftiext(self.obase)+'.par')
            os.remove(fileutils.removeniftiext(self.obase)+'.nii.gz')
        elif (self.name == 'seedconn'):
            os.remove(fileutils.removeniftiext(self.obase)+'_pearsonr.nii.gz')
            os.remove(fileutils.removeniftiext(self.obase)+'_tval.nii.gz')
        elif (self.name == 'ssmooth'):
            os.remove(fileutils.removeniftiext(self.obase)+'.nii.gz')
        elif (self.name == 'motcor'):
            os.remove(fileutils.removeniftiext(self.obase)+'.nii.gz')
            os.remove(fileutils.removeniftiext(self.obase)+'_brainmask.nii.gz')
            os.remove(fileutils.removeniftiext(self.obase)+'_mindisplacementInd_0ref_motbrick.txt')
        elif (self.name == 'retroicor'):
            os.remove(fileutils.removeniftiext(self.obase)+'.nii.gz')
        else:
            sys.exit('Error: preprocessing step not defined')    

