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
            process=subprocess.Popen(['3dretroicor', \
                                      '-prefix', fileutils.removeniftiext(self.obase), \
                                      '-ignore', self.params[self.params.index('-ignore')+1], \
                                      '-card', self.params[self.params.index('-card')+1], \
                                      '-resp', self.params[self.params.index('-resp')+1], \
                                      fileutils.addniigzext(self.ibase)])
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
                                      '-prefix',fileutils.removeniftiext(self.obase)+'_temp_brainmask', \
                                      fileutils.addniigzext(self.ibase)])
            (output,error)=process.communicate()
            fileutils.afni2nifti(fileutils.removeniftiext(self.obase)+'_temp_brainmask')
            # then use the mask to extract the 4D functional data
            p=subprocess.Popen(['fslmaths',self.ibase,\
                                '-mas',fileutils.removeniftiext(self.obase)+'_temp_brainmask',\
                                fileutils.removeniftiext(self.obase)])
            p.communicate()
            os.remove(fileutils.removeniftiext(self.obase)+'_temp_brainmask.nii.gz')

        elif (self.name == 'brainExtractFSL'):
            # first extract brain mask from a temporal mean volume
            p=subprocess.Popen(['fslmaths',self.ibase,'-Tmean',fileutils.removeniftiext(self.obase)+'_temp_tmean'])
            p.communicate()
            p=subprocess.Popen(['bet2',fileutils.removeniftiext(self.obase)+'_temp_tmean',\
                                fileutils.removeniftiext(self.obase)+'_temp_tmean',\
                                '-f','0.3','-n','-m']) # create a binary mask from the the mean image. (bet2 automatically adds a _mask suffix to the output file)
            p.communicate()
            # then use the mask to extract the 4D functional data
            p=subprocess.Popen(['fslmaths',self.ibase,\
                                '-mas',fileutils.removeniftiext(self.obase)+'_temp_tmean_mask',\
                                self.obase])
            p.communicate()
            os.remove(fileutils.removeniftiext(self.obase)+'_temp_tmean.nii.gz')
            os.remove(fileutils.removeniftiext(self.obase)+'_temp_tmean_mask.nii.gz')
            
        else:
            sys.exit('Error: preprocessing step not defined')
            
    def removeofiles(self):
        if (self.name == 'mcflirt'):
            os.remove(fileutils.removeniftiext(self.obase)+'.par')
            os.remove(fileutils.addniigzext(self.obase))
        elif (self.name == 'seedconn'):
            os.remove(fileutils.removeniftiext(self.obase)+'_pearsonr.nii.gz')
            os.remove(fileutils.removeniftiext(self.obase)+'_tval.nii.gz')
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
        else:
            sys.exit('Error: preprocessing step not defined')    


def makesteps(pipelinefile,data):
    steps=[]
    f=open(pipelinefile)
    line=f.readline()
    s=line.split()
    while len(s)>0:
        name=s[0]
        params=s[1:]
        if s[0]=='retroicor':
            if data.card != '':
                params.append('-card')
                params.append(data.card)
            if data.resp != '':
                params.append('-resp')
                params.append(data.resp)        
        step=PreprocessingStep(name,params)
        steps.append(step)
        line=f.readline()
        s=line.split()
    return(steps)

def permutations(l):
    if len(l) <= 1:
        yield(l)
    else:
        for p in permutations(l[1:]):
            for i in range(len(l)):
                yield(p[:i]+l[0:1]+p[i:])

def onoff(l):
    if len(l) <= 1:
        yield(l)
        yield([])
    else:
        for p in onoff(l[1:]):
            yield(l[0:1]+p)
            yield(p)

def concatstepslists(l1,l2):
    # NOTE: inputs must be lists of lists NOT generators
    for p1 in l1:
        for p2 in l2:
            yield(p1+p2)

