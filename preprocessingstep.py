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
        if (self.name == 'mcflirt'):
            process=subprocess.Popen(['mcflirt','-in',self.ibase,'-out',self.obase,'-plots'])
            (output,error)=process.communicate()
        elif (self.name == 'seedconn'):
            seedcorr.calcseedcorr(fileutils.addniigzext(self.ibase), \
                                  self.params[0], \
                                  fileutils.addniigzext(self.obase))
        else:
            sys.exit('Error: preprocessing step not defined')
            
    def removeofiles(self):
        if (self.name == 'mcflirt'):
            os.remove(fileutils.removeniftiext(self.obase)+'.par')
            os.remove(fileutils.removeniftiext(self.obase)+'.nii.gz')
        elif (self.name == 'seedconn'):
            os.remove(fileutils.addniigzext(self.obase))
        else:
            sys.exit('Error: preprocessing step not defined')    

