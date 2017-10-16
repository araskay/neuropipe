import subprocess # used to run bash commands
import sys
import seedcorr
import fileutils
import os
import nibabel

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
            if self.data.motpar == '':
                self.data.motpar=fileutils.removeniftiext(self.obase)+'.par'
            else:
                os.remove(fileutils.removeniftiext(self.obase)+'.par')
        
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
            os.remove(fileutils.removeniftiext(self.obase)+'_temp_brainmask.nii.gz')
            os.remove(fileutils.removeniftiext(self.obase)+'_temp_mindisplacementInd_0ref_motbrick.txt')
            
        elif (self.name == 'retroicor'):
            physparams=[]
            if self.data.card != '':
                physparams.append('-card')
                physparams.append(self.data.card)
            if self.data.resp != '':
                physparams.append('-resp')
                physparams.append(self.data.resp)            
            process=subprocess.Popen(['3dretroicor', '-prefix', fileutils.removeniftiext(self.obase)]+ \
                                     self.params + physparams + \
                                     [fileutils.addniigzext(self.ibase)])
            (output,error)=process.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase))           
        
        elif (self.name == '3dSkullStrip'):
            process=subprocess.Popen(['3dSkullStrip',\
                                      '-input',fileutils.addniigzext(self.ibase),\
                                      '-prefix', fileutils.removeniftiext(self.obase)])
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
                                      '-prefix',fileutils.removeniftiext(self.obase)+'__brainmask', \
                                      fileutils.addniigzext(self.ibase)])
            (output,error)=process.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase)+'__brainmask')
            # then use the mask to extract the 4D functional data
            p=subprocess.Popen(['fslmaths',self.ibase,\
                                '-mas',fileutils.removeniftiext(self.obase)+'__brainmask',\
                                fileutils.removeniftiext(self.obase)])
            p.communicate()
            if self.data.brainmask == '':
                self.data.brainmask = fileutils.removeniftiext(self.obase)+'__brainmask.nii.gz'
            else:
                os.remove(fileutils.removeniftiext(self.obase)+'__brainmask.nii.gz')

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
            os.remove(fileutils.removeniftiext(self.obase)+'__tmean.nii.gz')
            if self.data.brainmask == '':
                self.data.brainmask=fileutils.removeniftiext(self.obase)+'__tmean_mask.nii.gz'
            else:
                os.remove(fileutils.removeniftiext(self.obase)+'__tmean_mask.nii.gz')
            
        elif (self.name == '3dFourier'):
            p=subprocess.Popen(['3dFourier']+self.params+\
                               ['-prefix',fileutils.removeniftiext(self.obase),fileutils.addniigzext(self.ibase)])
            p.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase))                         
         
        elif (self.name == 'motreg'):
            if self.data.motpar=='':
                sys.exit('Cannot run regmot- no motion parameters available. Need to either provide motion parameters or have mcflirt run before regmot')
            p=subprocess.Popen(['fsl_glm','-i',self.ibase,\
                                '-d',self.data.motpar,\
                                '-o',fileutils.removeniftiext(self.obase)+'__motglm',
                                '--out_res='+self.obase])
            p.communicate()
            if self.data.motglm=='':
                self.data.motglm=fileutils.removeniftiext(self.obase)+'__motglm'
            else:
                os.remove(fileutils.removeniftiext(self.obase)+'__motglm.nii.gz')
        
        elif self.name=='tmean':
            p=subprocess.Popen(['fslmaths',self.ibase,'-Tmean',self.obase])
            p.communicate()
        
        elif self.name=='slicetimer':
            # get the TR from the data
            img_nib=nibabel.load(fileutils.addniigzext(self.ibase))
            hdr=img_nib.header
            tr=str(hdr.get_zooms()[3])
            p=subprocess.Popen(['slicetimer','-i',self.ibase,'-o',self.obase,'-r',tr]+self.params)
            p.communicate()                


        elif self.name=='stcor':
            # get the TR from the data
            img_nib=nibabel.load(fileutils.addniigzext(self.ibase))
            hdr=img_nib.header
            tr=str(hdr.get_zooms()[3]*1000)
            if len(self.data.slicetiming)>0:
                p=subprocess.Popen(['3dTshift','-TR',tr,'-tpattern','@'+self.data.slicetiming,\
                                    '-prefix',fileutils.removext(self.obase), fileutils.addniigzext(self.ibase)])
                p.communicate()
                fileutils.afni2nifti(fileutils.removeniftiext(self.obase))
            else:
                sys.exit('Please provide slice timing offsets for slice timing correction.')                
                
        else:
            sys.exit('Error: preprocessing step not defined')      
         
    def removeofiles(self):
        if (self.name == 'mcflirt'):
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == 'ssmooth'):
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == 'motcor'):
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == 'retroicor'):
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == '3dSkullStrip'):
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == 'bet'):
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == 'fslreorient2std'):
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == 'brainExtractAFNI'):
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == 'brainExtractFSL'):
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == '3dFourier'):
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == 'motreg'):
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == 'tmean'):
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == 'slicetimer'):
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == 'stcor'):
            os.remove(fileutils.addniigzext(self.obase))
        else:
            sys.exit('Error: preprocessing step not defined')    


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

def permutations(l):
    if 0 < len(l) <= 1:
        yield(l)
    elif len(l)>1:
        for p in permutations(l[1:]):
            for i in range(len(l)):
                yield(p[:i]+l[0:1]+p[i:])

def onoff(l):
    if 0 < len(l) <= 1:
        yield(l)
        yield([])
    elif len(l)>1:
        for p in onoff(l[1:]):
            yield(l[0:1]+p)
            yield(p)

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

