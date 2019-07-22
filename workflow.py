# Includes definition of the following classes and their routines:
# - EnvVars
# - Data
# - BetweenSubjectMetrics
# - Run
# - Session
# - Subject
# - Workflow
# Also includes functions to read and save subjects to/from text-based subjects files
# Report bugs/issues to M. Aras Kayvanrad (mkayvan@gmail.com).
# (c) M. Aras Kayvanrad

import sys
import spmsim
import fileutils
import getopt,shlex
import subprocess
import numpy as np

pthresh=0.05 # significance level for thresholding seed connectivity maps

class EnvVars:
    def __init__(self):
        self.mni152=''
        self.boldregdof='12'
        self.structregdof='12'
        self.boldregcost='corratio' # flirt default
        self.structregcost='corratio' #flirt default
        self.maskthresh='0.5'

class Data:
    def __init__(self):
        self.bold=''
        self.structural=''
        self.structuralbrainmask=''
        self.card=''
        self.resp=''
        self.opath=''
        self.connseed=''
        self.motpar=''
        self.brainmask=''
        self.glm=''
        self.siemensphysio=''
        self.biopacphysio=''
        self.sliceorder=''
        self.slicetiming=''
        #self.structuralcsfpve=''
        #self.structuralgmpve=''
        #self.structuralwmpve=''
        #self.structuralcsfseg=''
        #self.structuralgmseg=''
        #self.structuralwmseg=''
        self.structuralcsf=''
        self.structuralgm=''
        self.structuralwm=''
        #self.boldcsfpve=''
        #self.boldgmpve=''
        #self.boldwmpve=''
        #self.boldcsfseg=''
        #self.boldgmseg=''
        #self.boldwmseg=''
        self.boldcsf=''
        self.boldgm=''
        self.boldwm=''
        self.boldcsfwm=''      
        self.func2struct=''
        self.struct2func=''
        self.struct2mni=''
        self.mni2struct=''
        self.func2mni=''
        self.mni2func=''
        self.meants=''
        self.meantscsf=''
        self.meantsgm=''
        self.meantswm=''
        self.meantsnet=''
        self.meantscsfwm=''
        self.aseg=''
        self.wmseg=''
        self.regintermed=''
        self.boldtmean=''
        self.envvars=EnvVars()
        self.fsrecondir=''
        self.qa=''
        self.motmetric='' # motion metric file
        # regressors
        self.cardphase=''
        self.respphase=''
        self.acompPCs=''
        self.tcompPCs=''
        self.phycaaCompS1=''
        self.phycaaCompS2=''
        self.gsr=''
        self.csfwmr=''
        self.csfr=''
        self.wmr=''
        
    
    # this is not recommended anymore- use parcellate_structural
    def parcellate_mprage(self):
        if self.structural == '':
            sys.exit('Error in parcellate_mprage: Structural data not given. Cannot proceed without. Exiting!')            
        p=subprocess.Popen(['fast','-t','1','-n','3','--segments',\
                            '-o',fileutils.removext(self.structural),\
                            self.structural])
        p.communicate()
        #self.structuralcsfpve=fileutils.removext(self.structural)+'_pve_0.nii.gz'
        #self.structuralgmpve=fileutils.removext(self.structural)+'_pve_1.nii.gz'
        #self.structuralwmpve=fileutils.removext(self.structural)+'_pve_2.nii.gz'
        self.structuralcsf=fileutils.removext(self.structural)+'_seg_0.nii.gz'
        self.structuralgm=fileutils.removext(self.structural)+'_seg_1.nii.gz'
        self.structuralwm=fileutils.removext(self.structural)+'_seg_2.nii.gz' 
       
    def parcellate_structural(self):
        if self.structural == '':
            sys.exit('Error in parcellate_structural: Structural image not given. Cannot proceed without. Exiting!') 
        if self.aseg == '':
            print('In parcellate_structural: aseg not given. Stepping back to FSL FAST segmentation.')
            self.parcellate_mprage()
        else:
            p=subprocess.Popen(['mri_binarize','--i',self.aseg,'--o',fileutils.removext(self.structural)+'_csf.nii.gz','--match','0','--ventricles','--mask',self.structuralbrainmask])
            p.communicate()
            p=subprocess.Popen(['mri_binarize','--i',self.aseg,'--o',fileutils.removext(self.structural)+'_wm.nii.gz','--ctx-wm'])
            p.communicate()
            p=subprocess.Popen(['mri_binarize','--i',self.aseg,'--o',fileutils.removext(self.structural)+'_gm.nii.gz','--gm'])
            p.communicate()
            self.structuralcsf=fileutils.removext(self.structural)+'_csf.nii.gz'
            self.structuralwm=fileutils.removext(self.structural)+'_wm.nii.gz'
            self.structuralgm=fileutils.removext(self.structural)+'_gm.nii.gz'
            
    def parcellate_bold(self):
        if self.structuralcsf=='' or self.structuralgm=='' or self.structuralwm=='':
            self.parcellate_structural()
        if self.struct2func=='':
            self.transform_struct2func()
        
        p=subprocess.Popen(['flirt','-in',self.structuralcsf,\
                            '-ref',self.bold,\
                            '-applyxfm','-init',self.struct2func,\
                            '-out',fileutils.removext(self.bold)+'_csf'])
        p.communicate()
        p=subprocess.Popen(['fslmaths',fileutils.removext(self.bold)+'_csf','-thr',self.envvars.maskthresh,'-bin',fileutils.removext(self.bold)+'_csf'])
        p.communicate()
        self.boldcsf=fileutils.removext(self.bold)+'_csf.nii.gz'
        
        p=subprocess.Popen(['flirt','-in',self.structuralgm,\
                            '-ref',self.bold,\
                            '-applyxfm','-init',self.struct2func,\
                            '-out',fileutils.removext(self.bold)+'_gm'])
        p.communicate()
        p=subprocess.Popen(['fslmaths',fileutils.removext(self.bold)+'_gm','-thr',self.envvars.maskthresh,'-bin',fileutils.removext(self.bold)+'_gm'])
        p.communicate()
        self.boldgm=fileutils.removext(self.bold)+'_gm.nii.gz'
        
        p=subprocess.Popen(['flirt','-in',self.structuralwm,\
                            '-ref',self.bold,\
                            '-applyxfm','-init',self.struct2func,\
                            '-out',fileutils.removext(self.bold)+'_wm'])
        p.communicate()         
        p=subprocess.Popen(['fslmaths',fileutils.removext(self.bold)+'_wm','-thr',self.envvars.maskthresh,'-bin',fileutils.removext(self.bold)+'_wm'])
        p.communicate()
        self.boldwm=fileutils.removext(self.bold)+'_wm.nii.gz'          

        # combine csf and wm rois into one roi
        p=subprocess.Popen(['fslmaths',self.boldcsf,'-add',self.boldwm,'-bin',fileutils.removext(self.bold)+'_csfwm'])
        p.communicate()
        self.boldcsfwm=fileutils.removext(self.bold)+'_csfwm.nii.gz'
    
    def calc_meants(self):
        
        if self.boldcsf=='' or self.boldgm=='' or self.boldwm=='':
            self.parcellate_bold()
            
        if len(self.brainmask)>0:
            p=subprocess.Popen(['fslmeants','-i',self.bold,\
                                '-o',fileutils.removext(self.bold)+'_meants.txt',\
                                '-m',self.brainmask])
            p.communicate()
            self.meants=fileutils.removext(self.bold)+'_meants.txt'
        
        if len(self.boldcsf)>0:
            p=subprocess.Popen(['fslmeants','-i',self.bold,\
                                '-o',fileutils.removext(self.bold)+'_meants_csf.txt',\
                                '-m',self.boldcsf])
            p.communicate()
            self.meantscsf=fileutils.removext(self.bold)+'_meants_csf.txt'
            
        if len(self.boldgm)>0:
            p=subprocess.Popen(['fslmeants','-i',self.bold,\
                                '-o',fileutils.removext(self.bold)+'_meants_gm.txt',\
                                '-m',self.boldgm])
            p.communicate()
            self.meantsgm=fileutils.removext(self.bold)+'_meants_gm.txt'
        
        if len(self.boldwm)>0:
            p=subprocess.Popen(['fslmeants','-i',self.bold,\
                                '-o',fileutils.removext(self.bold)+'_meants_wm.txt',\
                                '-m',self.boldwm])
            p.communicate()        
            self.meantswm=fileutils.removext(self.bold)+'_meants_wm.txt'         
    
        if len(self.boldcsfwm)>0:
            p=subprocess.Popen(['fslmeants','-i',self.bold,\
                                '-o',fileutils.removext(self.bold)+'_meants_csfwm.txt',\
                                '-m',self.boldcsfwm])
            p.communicate()        
            self.meantscsfwm=fileutils.removext(self.bold)+'_meants_csfwm.txt'              
    
    def calc_boldtmean(self):
        p=subprocess.Popen(['fslmaths',self.bold,'-Tmean',fileutils.removext(self.bold)+'_tmean'])
        p.communicate()
        self.boldtmean=fileutils.removext(self.bold)+'_tmean'
    
    def transform_func2struct(self):
        if self.structural == '':
            sys.exit('Error in func2struct: Structural data not given. Cannot proceed without. Exiting!')
        
        if self.func2struct=='':
            self.calc_boldtmean()
            p=subprocess.Popen(['flirt','-in',self.boldtmean,\
                                '-ref',self.structural,\
                                '-dof',self.envvars.boldregdof,\
                                '-cost',self.envvars.boldregcost,\
                                '-out',fileutils.removext(self.boldtmean)+'_func2struct',\
                                '-omat',fileutils.removext(self.bold)+'_func2struct.mat']) 
            p.communicate()

            self.func2struct=fileutils.removext(self.bold)+'_func2struct.mat'

        p=subprocess.Popen(['flirt','-in',self.bold,\
                            '-ref',self.structural,\
                            '-applyxfm','-init',self.func2struct,\
                            '-out',fileutils.removext(self.bold)+'_func2struct'])
        p.communicate()            
  
                
    def transform_struct2func(self):
        if self.struct2func=='':
            if self.func2struct=='':
                self.transform_func2struct()
            p=subprocess.Popen(['convert_xfm','-inverse','-omat',fileutils.removext(self.bold)+'_struct2func.mat',\
                                self.func2struct])
            p.communicate()
            self.struct2func=fileutils.removext(self.bold)+'_struct2func.mat'         

        p=subprocess.Popen(['flirt','-in',self.structural,\
                            '-ref',self.bold,\
                            '-applyxfm','-init',self.struct2func,\
                            '-out',fileutils.removext(self.structural)+'_struct2func'])
        p.communicate()             
    
    def transform_struct2mni(self):
        if self.envvars.mni152=='':
            sys.exit('Error in struct2mni: MNI152 environment variable not set. Exiting!')
        
        if self.struct2mni=='':
            p=subprocess.Popen(['flirt','-in',self.structural,\
                                '-ref',self.envvars.mni152,\
                                '-dof',self.envvars.structregdof,\
                                '-cost',self.envvars.structregcost,\
                                '-out',fileutils.removext(self.structural)+'_struct2mni',\
                                '-omat',fileutils.removext(self.structural)+'_struct2mni.mat'])
            p.communicate()
            self.struct2mni=fileutils.removext(self.structural)+'_struct2mni.mat'
        else:
            p=subprocess.Popen(['flirt','-in',self.structural,\
                                '-ref',self.envvars.mni152,\
                                '-applyxfm','-init',self.struct2mni,\
                                '-out',fileutils.removext(self.structural)+'_struct2mni'])
            p.communicate()
        
    def transfrom_mni2struct(self):
        if self.mni2struct=='':
            if self.struct2mni=='':
                self.transform_struct2mni()
            p=subprocess.Popen(['convert_xfm','-inverse','-omat',fileutils.removext(self.structural)+'_mni2struct.mat',\
                                self.struct2mni])
            p.communicate()
            self.mni2struct=fileutils.removext(self.structural)+'_mni2struct.mat' 
        
    def transform_func2mni(self):
        if self.func2mni=='':
            self.transform_func2struct()
            self.transform_struct2mni()

            p=subprocess.Popen(['convert_xfm','-omat',fileutils.removext(self.bold)+'_func2mni.mat',\
                                '-concat',self.struct2mni,self.func2struct])
            p.communicate()
            self.func2mni=fileutils.removext(self.bold)+'_func2mni.mat'
        p=subprocess.Popen(['flirt','-in',self.bold,\
                            '-ref',self.envvars.mni152,\
                            '-applyxfm','-init',self.func2mni,\
                            '-out',fileutils.removext(self.bold)+'_func2mni'])
        p.communicate()

    def transform_mni2func(self):
        if self.mni2func=='':
            if self.func2mni=='':
                self.transform_func2mni()

            p=subprocess.Popen(['convert_xfm','-inverse','-omat',fileutils.removext(self.bold)+'_mni2func.mat',\
                                fileutils.removext(self.bold)+'_func2mni.mat'])
            p.communicate()        
            self.mni2func=fileutils.removext(self.bold)+'_mni2func.mat'

class Run:
    def __init__(self,seqname,data):
        self.seqname=seqname
        self.data=data
        self.pipelines=[]
        self.optimalpipeline=None
        self.optimalpipeline_r=None
        self.optimalpipeline_j=None
        self.optimalpipeline_rj=None
        
    def setpipelines(self,pipelines):
        self.pipelines=pipelines
    
    def addpipeline(self,pipeline):
        self.pipelines.append(pipeline)
        
    def process(self):
        if (self.pipelines == []):
            sys.exit('Error: No pipelines set for the run. Set pipelines before calling process()')
        for pipe in self.pipelines:
            pipe.run()
            
    def parcellate(self):
        if (self.pipelines == []):
            sys.exit('Error: No pipelines set for the run. Set pipelines before calling process()')
        for pipe in self.pipelines:
            pipe.parcellate()

    def meants(self):
        if (self.pipelines == []):
            sys.exit('Error: No pipelines set for the run. Set pipelines before calling process()')
        for pipe in self.pipelines:
            pipe.meants()
            
    def seedconn(self):
        if (self.pipelines == []):
            sys.exit('Error: No pipelines set for the run. Set pipelines before calling process()')
        for pipe in self.pipelines:
            pipe.calcseedconn(pthresh)
            
    
    def tomni(self):
        if (self.pipelines == []):
            sys.exit('Error: No pipelines set for the run. Set pipelines before calling process()')
        for pipe in self.pipelines:
            pipe.output2mni()
            if pipe.seedconncomputed:
                pipe.seedconn2mni()
                        
class Session:
    def __init__(self,ID):
        self.ID=ID
        self.runs=[]
        
    def addrun(self,run):
        self.runs.append(run)
  
class Subject:
    def __init__(self,ID):
        self.ID=ID
        self.sessions=[]
       
    def addsession(self,session):
        self.sessions.append(session)
        
class Workflow:
    def __init__(self,name):
        self.name=name
        self.subjects=[]
        self.optimalpipelinesfound=False
        self.betweensubject=None
        self.parcellate=False
        self.seedconn=False
        self.meants=False
        self.tomni=False
    
    def addsubject(self,subject):
        self.subjects.append(subject)
        
    def run(self):
        if (self.subjects == []):
            sys.exit('Error: no subjects to process')
        for subj in self.subjects:
            for sess in subj.sessions:
                for run in sess.runs:
                    run.process()
                    if self.seedconn:
                        run.seedconn()
                    if self.parcellate:
                        run.parcellate()
                    if self.meants:
                        run.meants()
                    if self.tomni:
                        run.tomni() # this should happen after run.seedconn()
        
def getsubjects(subjectfile):
    subjects=[]
    f=open(subjectfile)
    line=f.readline()
    l=shlex.split(line)
    while len(l)>0:
        subjectID=''
        sessionID=''
        sequence=''       
        data=Data()
        try:
            (opts,_) = getopt.getopt(l,'',['subjectID=',\
                                              'sessionID=',\
                                              'bold=',\
                                              'structural=',\
                                              'structuralbrainmask=',\
                                              'card=',\
                                              'resp=',\
                                              'opath=',\
                                              'sequence=',\
                                              'connseed=',\
                                              'motpar=',\
                                              'brainmask=',\
                                              'glm=',\
                                              'motglm=',\
                                              'siemensphysio=',\
                                              'biopacphysio=',\
                                              'aseg=',\
                                              'wmseg=',\
                                              'regintermed=',\
                                              'slicetiming=',\
                                              'sliceorder=',\
                                              'func2struct=',\
                                              'struct2func=',\
                                              'struct2mni=',\
                                              'mni2struct=',\
                                              'func2mni=',\
                                              'mni2func=',\
                                              'fsrecondir=',\
                                              'structuralcsf=',\
                                              'structuralgm=',\
                                              'structuralwm=',\
                                              'boldgm=',\
                                              'boldwm=',\
                                              'boldcsf=',\
                                              'boldcsfwm=',\
                                              'meants=',\
                                              'meantswm=',\
                                              'meantsgm=',\
                                              'meantscsf=',\
                                              'meantscsfwm=',\
                                              'qa=',\
                                              'motmetric=',\
                                              'cardphase=',\
                                              'respphase=',\
                                              'acompPCs=',\
                                              'tcompPCs=',\
                                              'phycaaCompS1=',\
                                              'phycaaCompS2=',\
                                              'gsr=',\
                                              'csfwmr=',\
                                              'csfr=',\
                                              'wmr='])
        except getopt.GetoptError:
            sys.exit('Error in subjects file format. Please check the option identifiers in the subjects file. Also please note that identifiers require double dash (--)')
        for (opt,arg) in opts:
            if opt in ('--subjectID'):
                subjectID=arg
            elif opt in ('--sessionID'):
                sessionID=arg
            elif opt in ('--sequence'):
                sequence=arg                
            elif opt in ('--bold'):
                data.bold=arg
            elif opt in ('--structural'):
                data.structural=arg
            elif opt in ('--structuralbrainmask'):
                data.structuralbrainmask=arg
            elif opt in ('--card'):
                data.card=arg
            elif opt in ('--resp'):
                data.resp=arg
            elif opt in ('--opath'):
                data.opath=arg
            elif opt in ('--connseed'):
                data.connseed=arg
            elif opt in ('--motpar'):
                data.motpar=arg
            elif opt in ('--brainmask'):
                data.brainmask=arg
            elif opt in ('--glm'):
                data.glm=arg
            elif opt in ('--motglm'):
                data.glm=arg # for backwards compatibility, save in glm not in motglm
            elif opt in ('--siemensphysio'):
                data.siemensphysio=arg
            elif opt in ('--biopacphysio'):
                data.biopacphysio=arg
            elif opt in ('--slicetiming'):
                data.slicetiming=arg
            elif opt in ('--sliceorder'):
                data.sliceorder=arg
            elif opt in ('--aseg'):
                data.aseg=arg
            elif opt in ('--wmseg'):
                data.wmseg=arg
            elif opt in ('--regintermed'):
                data.regintermed=arg
            elif opt in ('--func2struct'):
                data.func2struct=arg
            elif opt in ('--struct2func'):
                data.struct2func=arg
            elif opt in ('--struct2mni'):
                data.struct2mni=arg
            elif opt in ('--mni2struct'):
                data.mni2struct=arg
            elif opt in ('--func2mni'):
                data.func2mni=arg
            elif opt in ('--mni2func'):
                data.mni2func=arg
            elif opt in ('--fsrecondir'):
                data.fsrecondir=arg
            elif opt in ('--structuralcsf'):
                data.structuralcsf=arg
            elif opt in ('--structuralgm'):
                data.structuralgm=arg
            elif opt in ('--structuralwm'):
                data.structuralwm=arg
            elif opt in ('--boldgm'):
                data.boldgm=arg
            elif opt in ('--boldwm'):
                data.boldwm=arg
            elif opt in ('--boldcsf'):
                data.boldcsf=arg
            elif opt in ('--boldcsfwm'):
                data.boldcsfwm=arg                
            elif opt in ('--meants'):
                data.meants=arg
            elif opt in ('--meantsgm'):
                data.meantsgm=arg 
            elif opt in ('--meantswm'):
                data.meantswm=arg 
            elif opt in ('--meantscsf'):
                data.meantscsf=arg
            elif opt in ('--meantscsfwm'):
                data.meantscsfwm=arg
            elif opt in ('--qa'):
                data.qa=arg
            elif opt in ('--motmetric'):
                data.motmetric=arg
            elif opt in ('--cardphase'):
                data.cardphase=arg
            elif opt in ('--respphase'):
                data.respphase=arg
            elif opt in ('--acompPCs'):
                data.acompPCs=arg
            elif opt in ('--tcompPCs'):
                data.tcompPCs=arg
            elif opt in ('--phycaaCompS1'):
                data.phycaaCompS1=arg
            elif opt in ('--phycaaCompS2'):
                data.phycaaCompS2=arg
            elif opt in ('--gsr'):
                data.gsr=arg
            elif opt in ('--csfwmr'):
                data.csfwmr=arg
            elif opt in ('--csfr'):
                data.csfr=arg
            elif opt in ('--wmr'):
                data.wmr=arg

        run=Run(sequence,data)
        matchsubj=[s for s in subjects if len(s.ID)>0 and s.ID==subjectID ] # only match if there is actually a subjectID, i.e., len(s.ID)>0
        if len(matchsubj)>0:
            subject=matchsubj[0]
        else:
            subject=Subject(subjectID)
            subjects.append(subject)
        matchsess=[s for s in subject.sessions if len(s.ID)>0 and s.ID==sessionID] # only match if there is actually a sessionID, i.e., len(s.ID)>0
        if len(matchsess)>0:
            session=matchsess[0]
            session.addrun(run)
        else:
            session=Session(sessionID)
            session.addrun(run)
            subject.addsession(session)
        line=f.readline()
        l=shlex.split(line)
    return(subjects)

def savesubjects(filename,subjects,append=True):
    if append:
        f=open(filename, 'a')
    else:
        f=open(filename, 'w')
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                f.write('--subjectID \''+subj.ID+'\' '+\
                        '--sessionID \''+sess.ID+'\' '+\
                        '--sequence \''+run.seqname+'\' '+\
                        '--bold \''+run.data.bold+'\' '+\
                        '--structural \''+run.data.structural+'\' '+\
                        '--structuralbrainmask \''+run.data.structuralbrainmask+'\' '+\
                        '--card \''+run.data.card+'\' '+\
                        '--resp \''+run.data.resp+'\' '+\
                        '--opath \''+run.data.opath+'\' '+\
                        '--connseed \''+run.data.connseed+'\' '+\
                        '--motpar \''+run.data.motpar+'\' '+\
                        '--brainmask \''+run.data.brainmask+'\' '+\
                        '--glm \''+run.data.glm+'\' '+\
                        '--siemensphysio \''+run.data.siemensphysio+'\' '+\
                        '--biopacphysio \''+run.data.biopacphysio+'\' '+\
                        '--slicetiming \''+run.data.slicetiming+'\' '+\
                        '--sliceorder \''+run.data.sliceorder+'\' '+\
                        '--fsrecondir \''+run.data.fsrecondir+'\' '+\
                        '--aseg \''+run.data.aseg+'\' '+\
                        '--wmseg \''+run.data.wmseg+'\' '+\
                        '--regintermed \''+run.data.regintermed+'\' '+\
                        '--func2struct \''+run.data.func2struct+'\' '+\
                        '--struct2func \''+run.data.struct2func+'\' '+\
                        '--struct2mni \''+run.data.struct2mni+'\' '+\
                        '--mni2struct \''+run.data.mni2struct+'\' '+\
                        '--func2mni \''+run.data.func2mni+'\' '+\
                        '--mni2func \''+run.data.mni2func+'\' '+\
                        '--structuralcsf \''+run.data.structuralcsf+'\' '+\
                        '--structuralgm \''+run.data.structuralgm+'\' '+\
                        '--structuralwm \''+run.data.structuralwm+'\' '+\
                        '--boldgm \''+run.data.boldgm+'\' '+\
                        '--boldwm \''+run.data.boldwm+'\' '+\
                        '--boldcsf \''+run.data.boldcsf+'\' '+\
                        '--boldcsfwm \''+run.data.boldcsfwm+'\' '+\
                        '--meants \''+run.data.meants+'\' '+\
                        '--meantsgm \''+run.data.meantsgm+'\' '+\
                        '--meantswm \''+run.data.meantswm+'\' '+\
                        '--meantscsf \''+run.data.meantscsf+'\' '+\
                        '--meantscsfwm \''+run.data.meantscsfwm+'\' '+\
                        '--qa \''+run.data.qa+'\' '+\
                        '--motmetric \''+run.data.motmetric+'\' '+\
                        '--cardphase \''+run.data.cardphase+'\' '+\
                        '--respphase \''+run.data.respphase+'\' '+\
                        '--acompPCs \''+run.data.acompPCs+'\' '+\
                        '--tcompPCs \''+run.data.tcompPCs+'\' '+\
                        '--phycaaCompS1 \''+run.data.phycaaCompS1+'\' '+\
                        '--phycaaCompS2 \''+run.data.phycaaCompS2+'\' '+\
                        '--gsr \''+run.data.gsr+'\' '+\
                        '--csfwmr \''+run.data.csfwmr+'\' '+\
                        '--csfr \''+run.data.csfr+'\' '+\
                        '--wmr \''+run.data.wmr+'\' '+\
                        '\n')
    f.close()
    

                        
