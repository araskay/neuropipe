import sys
import spmsim
import fileutils
import getopt,shlex
import os,subprocess,nibabel, copy
from preprocessingstep import PreprocessingStep
import numpy as np

pthresh=0.05 # significance level for thresholding seed connectivity maps

class EnvVars:
    def __init__(self):
        self.mni152=''
        self.boldregdof='12'
        self.structregdof='12'

class Data:
    def __init__(self):
        self.bold=''
        self.structural=''
        self.card=''
        self.resp=''
        self.opath=''
        self.connseed=''
        self.motpar=''
        self.brainmask=''
        self.motglm=''
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
        self.func2struct=''
        self.struct2func=''
        self.struct2mni=''
        self.mni2struct=''
        self.func2mni=''
        self.mni2func=''
        self.meantscsf=''
        self.meantsgm=''
        self.meantswm=''
        self.meantsnet=''
        self.imeantscsf=''
        self.imeantsgm=''
        self.imeantswm=''
        self.imeantsnet=''
        self.aseg=''
        self.wmseg=''
        self.regintermed=''
        self.envvars=EnvVars()
    
    # this is not recommended anymore- use parcellate_structural
    def parcellate_mprage(self):
        if self.structural == '':
            sys.exit('In parcellate_mprage: Structural data not given. Cannot proceed without. Exiting!')            
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
            sys.exit('In parcellate_structural: Structural image not given. Cannot proceed without. Exiting!') 
        if self.aseg == '':
            print('In parcellate_structural: aseg not given. Stepping back to FSL FAST segmentation.')
            self.parcellate_mprage()
        else:
            p=subprocess.Popen(['mri_binarize','--i',self.aseg,'--o',fileutils.removext(self.structural)+'_csf.nii.gz','--ventricles'])
            p.communicate()
            p=subprocess.Popen(['mri_binarize','--i',self.aseg,'--o',fileutils.removext(self.structural)+'_wm.nii.gz','--ctx-wm'])
            p.communicate()
            p=subprocess.Popen(['mri_binarize','--i',self.aseg,'--o',fileutils.removext(self.structural)+'_gm.nii.gz','--gm'])
            p.communicate()
            self.structuralcsf=fileutils.removext(self.structural)+'_csf.nii.gz'
            self.structuralwm=fileutils.removext(self.structural)+'_wm.nii.gz'
            self.structuralgm=fileutils.removext(self.structural)+'_gm.nii.gz'
            
    def func2struct(self):
        if self.structural == '':
            sys.exit('In func2struct: Structural data not given. Cannot proceed without. Exiting!')
        if self.regintermed == '':
            p=subprocess.Popen(['flirt','-in',self.bold,\
                                '-ref',self.structural,\
                                '-dof',self.envvars.boldregdof,\
                                '-cost','bbr',\
                                '-out',fileutils.removext(self.bold)+'_func2struct',\
                                '-omat',fileutils.removext(self.output)+'_func2struct.mat']) 
            p.communicate()
        else:
            p=subprocess.Popen(['flirt','-in',self.bold,\
                                '-ref',self.regintermed,\
                                '-dof','3',\
                                '-cost','bbr',\
                                '-out',fileutils.removext(self.bold)+'__func2intermed',\
                                '-omat',fileutils.removext(self.bold)+'__func2intermed.mat']) 
            p.communicate()
            p=subprocess.Popen(['flirt','-in',self.data.regintermed,\
                                '-ref',self.data.structural,\
                                '-dof',self.envvars.boldregdof,\
                                '-cost','bbr',\
                                '-out',fileutils.removext(self.regintermed)+'__intermed2struct',\
                                '-omat',fileutils.removext(self.regintermed)+'__intermed2struct.mat']) 
            p.communicate()
            p=subprocess.Popen(['convert_xfm','-omat',fileutils.removext(self.bold)+'_func2struct.mat',\
                                '-concat',fileutils.removext(self.regintermed)+'__intermed2struct.mat',\
                                fileutils.removext(self.bold)+'__func2intermed.mat'])
            p.communicate()
            p=subprocess.Popen(['flirt','-in',self.bold,\
                                '-ref',self.data.structural,\
                                '-applyxfm','-init',fileutils.removext(self.bold)+'_func2struct.mat',\
                                '-out',fileutils.removext(self.bold)+'_func2struct'])
            p.communicate()
        self.data.func2struct=fileutils.removext(self.bold)+'_func2struct.mat'
        # while here, compute the inverse transform as well
        p=subprocess.Popen(['convert_xfm','-inverse','-omat',fileutils.removext(self.bold)+'_struct2func.mat',\
                            self.func2struct])
        p.communicate()
        self.data.struct2func=fileutils.removext(self.bold)+'_struct2func.mat'            
                
    def struct2mni(self):
        if self.envvars.mni152=='':
            sys.exit('In struct2mni: MNI152 environment variable not set. Exiting!')
        p=subprocess.Popen(['flirt','-in',self.structural,\
                            '-ref',self.envvars.mni152,\
                            '-dof',self.envvars.structregdof,\
                            '-out',fileutils.removext(self.structural)+'_struct2mni',\
                            '-omat',fileutils.removext(self.structural)+'_struct2mni.mat'])
        p.communicate()
        self.struct2mni=fileutils.removext(self.structural)+'_struct2mni.mat'
        # while here, compute the inverse transform as well
        p=subprocess.Popen(['convert_xfm','-inverse','-omat',fileutils.removext(self.structural)+'_mni2struct.mat',\
                            self.struct2mni])
        p.communicate()
        self.mni2struct=fileutils.removext(self.structural)+'_mni2struct.mat' 
        
    def func2mni(self):
        self.func2struct()
        self.struct2mni()

        p=subprocess.Popen(['convert_xfm','-omat',fileutils.removext(self.bold)+'_func2mni.mat',\
                            '-concat',self.struct2mni,self.func2sruct])
        p.communicate()
        self.func2mni=fileutils.removext(self.bold)+'_func2mni.mat'
        p=subprocess.Popen(['flirt','-in',self.bold,\
                            '-ref',self.envvars.mni152,\
                            '-applyxfm','-init',self.func2mni,\
                            '-out',fileutils.removext(self.bold)+'_func2mni'])
        p.communicate()     
        # while here, compute the inverse transform as well
        p=subprocess.Popen(['convert_xfm','-inverse','-omat',fileutils.removext(self.bold)+'_mni2func.mat',\
                            fileutils.removext(self.bold)+'_func2mni.mat'])
        p.communicate()        
        self.mni2func=fileutils.removext(self.bold)+'_mni2func.mat'

class BetweenSubjectMetrics:
    def __init__(self):
        self.reproducibility=0
        self.overlap=0
        self.reproducibility_r=0
        self.overlap_r=0
        self.reproducibility_j=0
        self.overlap_j=0
        self.reproducibility_rj=0
        self.overlap_rj=0
    
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
            pipe.seedconn2mni()
            
    def findoptimalpipeline(self):
        if (self.pipelines == []):
            sys.exit('Error: No pipelines set for the run. Set pipelines before calling findoptimalpipeline()')
        self.optimalpipeline=self.pipelines[0]
        self.optimalpipeline_r=self.pipelines[0]
        self.optimalpipeline_j=self.pipelines[0]
        self.optimalpipeline_rj=self.pipelines[0]
        for pipe in self.pipelines:
            pipe.calcsplithalfseedconnreproducibility()
            if (1-pipe.splithalfseedconnreproducibility) < (1-self.optimalpipeline.splithalfseedconnreproducibility):
                self.optimalpipeline=pipe
            if (1-pipe.splithalfseedconnreproducibility) < (1-self.optimalpipeline_r.splithalfseedconnreproducibility):
                self.optimalpipeline_r=pipe
            if (1-pipe.splithalfseedconnoverlap) < (1-self.optimalpipeline_j.splithalfseedconnoverlap):
                self.optimalpipeline_j=pipe
            if ((1-pipe.splithalfseedconnreproducibility)**2 + (1-pipe.splithalfseedconnoverlap)**2) < \
            ((1-self.optimalpipeline_rj.splithalfseedconnreproducibility)**2 + (1-self.optimalpipeline_rj.splithalfseedconnoverlap)**2):
                self.optimalpipeline_rj=pipe
 
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
    
    def addsubject(self,subject):
        self.subjects.append(subject)
        
    def initbetweensubject(self):
        self.betweensubject=np.empty((len(self.subjects),len(self.subjects)),dtype=object)
        for i in np.arange(self.betweensubject.shape[0]):
            for j in np.arange(self.betweensubject.shape[1]):
                metrics=BetweenSubjectMetrics()
                self.betweensubject[i,j]=metrics
    
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
                    
        
    def findoptimalpipelines(self):
        if (self.subjects == []):
            sys.exit('Error: no subjects to process')
        for subj in self.subjects:
            for sess in subj.sessions:
                for run in sess.runs:
                    run.findoptimalpipeline()
                    if self.parcellate:
                        if not run.optimalpipeline_r.parcellated:
                            run.optimalpipeline_r.parcellate()
                        if not run.optimalpipeline_j.parcellated:
                            run.optimalpipeline_j.parcellate()
                        if not run.optimalpipeline_rj.parcellated:
                            run.optimalpipeline_rj.parcellate()
                    if self.seedconn:
                        if not run.optimalpipeline_r.seedconncomputed:
                            run.optimalpipeline_r.calcseedconn(pthresh)
                        if not run.optimalpipeline_j.seedconncomputed:
                            run.optimalpipeline_j.calcseedconn(pthresh)
                        if not run.optimalpipeline_rj.seedconncomputed:
                            run.optimalpipeline_rj.calcseedconn(pthresh)
                    if self.meants:
                        if not run.optimalpipeline_r.meantscomputed:
                            run.optimalpipeline_r.meants()
                        if not run.optimalpipeline_j.meantscomputed:
                            run.optimalpipeline_j.meants()
                        if not run.optimalpipeline_rj.meantscomputed:
                            run.optimalpipeline_rj.meants()                            
        self.optimalpipelinesfound=True
        
    def computebetweensubjectreproducibility(self,seqName):
        # compute between subject reproducibility for the given seqName
        if not self.optimalpipelinesfound:
            self.findoptimalpipelines()
        count=0
        avgr=0
        if not self.betweensubject:
            self.initbetweensubject()
        for i in range(0,len(self.subjects)):
            for j in range(i+1,len(self.subjects)):
                subj1=self.subjects[i]
                subj2=self.subjects[j]
                ## implement averaging over sesssions
                for sess1 in subj1.sessions:
                    for sess2 in subj2.sessions:
                        # find the runs that match seqName
                        run1=[r for r in sess1.runs if r.seqname==seqName]
                        run2=[r for r in sess2.runs if r.seqname==seqName]
                        if len(run1)>0 and len(run2)>0:
                            count = count + 1
                            run1=run1[0] # assume there is only one run that matches
                            run2=run2[0] # same here
                            
                            if run1.optimalpipeline_r.seedconnz=='':
                                run1.optimalpipeline_r.calcseedconn(pthresh)
                            if run1.optimalpipeline_r.seedconnzmni152=='':
                                run1.optimalpipeline_r.seedconn2mni()
                            if run2.optimalpipeline_r.seedconnz=='':
                                run2.optimalpipeline_r.calcseedconn(pthresh)
                            if run2.optimalpipeline_r.seedconnzmni152=='':
                                run2.optimalpipeline_r.seedconn2mni()
                            r_r=spmsim.pearsoncorr(run1.optimalpipeline_r.seedconnzmni152,\
                                                   run2.optimalpipeline_r.seedconnzmni152)
                            jind_r=spmsim.jaccardind(run1.optimalpipeline_r.seedconnzthreshmni152,\
                                                     run2.optimalpipeline_r.seedconnzthreshmni152)

                            if run1.optimalpipeline_j.seedconnz=='':
                                run1.optimalpipeline_j.calcseedconn(pthresh)
                            if run1.optimalpipeline_j.seedconnzmni152=='':
                                run1.optimalpipeline_j.seedconn2mni()
                            if run2.optimalpipeline_j.seedconnz=='':
                                run2.optimalpipeline_j.calcseedconn(pthresh)
                            if run2.optimalpipeline_j.seedconnzmni152=='':
                                run2.optimalpipeline_j.seedconn2mni()
                            r_j=spmsim.pearsoncorr(run1.optimalpipeline_j.seedconnzmni152,\
                                                   run2.optimalpipeline_j.seedconnzmni152)
                            jind_j=spmsim.jaccardind(run1.optimalpipeline_j.seedconnzthreshmni152,\
                                                     run2.optimalpipeline_j.seedconnzthreshmni152)

                            if run1.optimalpipeline_rj.seedconnz=='':
                                run1.optimalpipeline_rj.calcseedconn(pthresh)
                            if run1.optimalpipeline_rj.seedconnzmni152=='':
                                run1.optimalpipeline_rj.seedconn2mni()
                            if run2.optimalpipeline_rj.seedconnz=='':
                                run2.optimalpipeline_rj.calcseedconn(pthresh)
                            if run2.optimalpipeline_rj.seedconnzmni152=='':
                                run2.optimalpipeline_rj.seedconn2mni()
                            r_rj=spmsim.pearsoncorr(run1.optimalpipeline_rj.seedconnzmni152,\
                                                    run2.optimalpipeline_rj.seedconnzmni152)
                            jind_rj=spmsim.jaccardind(run1.optimalpipeline_rj.seedconnzthreshmni152,\
                                                      run2.optimalpipeline_rj.seedconnzthreshmni152)
                                                      
                            # save the result as a BetweenSubject struct
                            '''self.betweensubject[i,j].reproducibility=r
                            self.betweensubject[i,j].overlap=jind'''
                            self.betweensubject[i,j].reproducibility_r=r_r
                            self.betweensubject[i,j].overlap_r=jind_r
                            self.betweensubject[i,j].reproducibility_j=r_j
                            self.betweensubject[i,j].overlap_j=jind_j
                            self.betweensubject[i,j].reproducibility_rj=r_rj
                            self.betweensubject[i,j].overlap_rj=jind_rj
                            # populate the lower triangle symmetrically
                            '''self.betweensubject[j,i].reproducibility=r
                            self.betweensubject[j,i].overlap=jind'''
                            self.betweensubject[j,i].reproducibility_r=r_r
                            self.betweensubject[j,i].overlap_r=jind_r
                            self.betweensubject[j,i].reproducibility_j=r_j
                            self.betweensubject[j,i].overlap_j=jind_j
                            self.betweensubject[j,i].reproducibility_rj=r_rj
                            self.betweensubject[j,i].overlap_rj=jind_rj                            
                            
    def saveallpipes(self,filename):
        # save all pipelines in csv format
        f=open(filename,'w')
        f.write('Subject_Sesssion_Run,PipeName,PipeSteps,SHReproducibility,SHOverlap\n')
        for subj in self.subjects:
            for sess in subj.sessions:
                for run in sess.runs:
                    for pipe in run.pipelines:
                        f.write(subj.ID+'_'+sess.ID+'_'+run.seqname+','+\
                                pipe.name+','+pipe.getsteps()+','+\
                                str(pipe.splithalfseedconnreproducibility)+','+\
                                str(pipe.splithalfseedconnoverlap)+'\n')
        f.close()

    def saveoptimalpipes(self,filename):
        # save optimal pipelines in csv format
        f=open(filename,'w')
        f.write('Subject_Sesssion_Run,OptMetric,PipeName,PipeSteps,SHReproducibility,SHOverlap\n')
        for subj in self.subjects:
            for sess in subj.sessions:
                for run in sess.runs:
                    pipe=run.optimalpipeline_r
                    f.write(subj.ID+'_'+sess.ID+'_'+run.seqname+','+\
                            'r'+','+\
                            pipe.name+','+pipe.getsteps()+','+\
                            str(pipe.splithalfseedconnreproducibility)+','+\
                            str(pipe.splithalfseedconnoverlap)+'\n')
                    pipe=run.optimalpipeline_j
                    f.write(subj.ID+'_'+sess.ID+'_'+run.seqname+','+\
                            'j'+','+\
                            pipe.name+','+pipe.getsteps()+','+\
                            str(pipe.splithalfseedconnreproducibility)+','+\
                            str(pipe.splithalfseedconnoverlap)+'\n')
                    pipe=run.optimalpipeline_rj
                    f.write(subj.ID+'_'+sess.ID+'_'+run.seqname+','+\
                            'rj'+','+\
                            pipe.name+','+pipe.getsteps()+','+\
                            str(pipe.splithalfseedconnreproducibility)+','+\
                            str(pipe.splithalfseedconnoverlap)+'\n')                    
        f.close()
      
    '''def printoptimalpipes(self):
        print('-----')
        print(self.name,'Otimal pipelines:')
        for subj in self.subjects:
            for sess in subj.sessions:
                for run in sess.runs:
                    print(subj.ID,'_',sess.ID,'_',run.seqname, \
                          'Optimal pipeline:',run.optimalpipeline.getsteps(), \
                          'S-H Reproducibility:',run.optimalpipeline.splithalfseedconnreproducibility)'''        
    
    def savebetweensubjectreproducibility_r(self,filename):
        f=open(filename,'w')
        f.write(',')
        for i in range(0,len(self.subjects)):
            f.write(self.subjects[i].ID+',')
        f.write('\n')
        for i in range(0,len(self.subjects)):
            f.write(self.subjects[i].ID+',')
            for j in range(0,len(self.subjects)):
                f.write(str(self.betweensubject[i,j].reproducibility_r)+',')
            f.write('\n')
        f.close()
        
    def savebetweensubjectreproducibility_j(self,filename):
        f=open(filename,'w')
        f.write(',')
        for i in range(0,len(self.subjects)):
            f.write(self.subjects[i].ID+',')
        f.write('\n')
        for i in range(0,len(self.subjects)):
            f.write(self.subjects[i].ID+',')
            for j in range(0,len(self.subjects)):
                f.write(str(self.betweensubject[i,j].reproducibility_j)+',')
            f.write('\n')
        f.close()
        
    def savebetweensubjectreproducibility_rj(self,filename):
        f=open(filename,'w')
        f.write(',')
        for i in range(0,len(self.subjects)):
            f.write(self.subjects[i].ID+',')
        f.write('\n')
        for i in range(0,len(self.subjects)):
            f.write(self.subjects[i].ID+',')
            for j in range(0,len(self.subjects)):
                f.write(str(self.betweensubject[i,j].reproducibility_rj)+',')
            f.write('\n')
        f.close()
        
    def savebetweensubjectoverlap_r(self,filename):
        f=open(filename,'w')
        f.write(',')
        for i in range(0,len(self.subjects)):
            f.write(self.subjects[i].ID+',')
        f.write('\n')
        for i in range(0,len(self.subjects)):
            f.write(self.subjects[i].ID+',')
            for j in range(0,len(self.subjects)):
                f.write(str(self.betweensubject[i,j].overlap_r)+',')
            f.write('\n')
        f.close()        
    
    def savebetweensubjectoverlap_j(self,filename):
        f=open(filename,'w')
        f.write(',')
        for i in range(0,len(self.subjects)):
            f.write(self.subjects[i].ID+',')
        f.write('\n')
        for i in range(0,len(self.subjects)):
            f.write(self.subjects[i].ID+',')
            for j in range(0,len(self.subjects)):
                f.write(str(self.betweensubject[i,j].overlap_j)+',')
            f.write('\n')
        f.close()
        
    def savebetweensubjectoverlap_rj(self,filename):
        f=open(filename,'w')
        f.write(',')
        for i in range(0,len(self.subjects)):
            f.write(self.subjects[i].ID+',')
        f.write('\n')
        for i in range(0,len(self.subjects)):
            f.write(self.subjects[i].ID+',')
            for j in range(0,len(self.subjects)):
                f.write(str(self.betweensubject[i,j].overlap_rj)+',')
            f.write('\n')
        f.close()

    def printbetweensubjectreproducibility(self):
        print('-----')
        print('-----')
        print(self.name,'Between subject reproducibility:')
        for i in range(0,len(self.subjects)):
            for j in range(i+1,len(self.subjects)):
                print(self.subjects[i].ID,'_',self.subjects[i].sessions[0].ID)
                print('Optimal r pipeline:')
                self.subjects[i].sessions[0].runs[0].optimalpipeline_r.printpipe()
                print('Optimal j pipeline:')
                self.subjects[i].sessions[0].runs[0].optimalpipeline_j.printpipe()
                print('Optimal rj pipeline:')
                self.subjects[i].sessions[0].runs[0].optimalpipeline_rj.printpipe()
                
                print(self.subjects[j].ID,'_',self.subjects[j].sessions[0].ID)
                print('Optimal r pipeline:')
                self.subjects[j].sessions[0].runs[0].optimalpipeline_r.printpipe()
                print('Optimal j pipeline:')
                self.subjects[j].sessions[0].runs[0].optimalpipeline_j.printpipe()
                print('Optimal rj pipeline:')
                self.subjects[j].sessions[0].runs[0].optimalpipeline_rj.printpipe()
                
                print('Between subject reproducibility (r-pipe): ',self.betweensubject[i,j].reproducibility_r)                
                print('Between subject overlap (r-pipe): ',self.betweensubject[i,j].overlap_r)
                print('Between subject reproducibility (j-pipe): ',self.betweensubject[i,j].reproducibility_j)                
                print('Between subject overlap (j-pipe): ',self.betweensubject[i,j].overlap_j)
                print('Between subject reproducibility (rj-pipe): ',self.betweensubject[i,j].reproducibility_rj)                
                print('Between subject overlap (rj-pipe): ',self.betweensubject[i,j].overlap_rj)
                print('-----')
        
def getsubjects(subjectfile):
    subjects=[]
    f=open(subjectfile)
    line=f.readline()
    l=shlex.split(line)
    while len(l)>0:
        subjectID=''
        sessionID=''
        bold=''
        card=''
        resp=''
        opath=''
        sequence=''
        structural=''
        connseed=''
        motpar=''
        brainmask=''
        motglm=''
        siemensphysio=''
        biopacphysio=''
        slicetiming=''
        sliceorder=''
        aseg=''
        wmseg=''
        regintermed=''
        try:
            (opts,args) = getopt.getopt(l,'',['subjectID=',\
                                              'sessionID=',\
                                              'bold=',\
                                              'structural=',\
                                              'card=',\
                                              'resp=',\
                                              'opath=',\
                                              'sequence=',\
                                              'connseed=',\
                                              'motpar=',\
                                              'brainmask=',\
                                              'motglm=',\
                                              'siemensphysio=',\
                                              'biopacphysio=',\
                                              'aseg=',\
                                              'wmseg=',\
                                              'regintermed=',\
                                              'slicetiming=',\
                                              'sliceorder='])
        except getopt.GetoptError:
            sys.exit('Error in subjects file format. Please check the option identifiers in the subjects file (e.g., subjects.txt). Also please note that identifiers require double dash (--)')
        for (opt,arg) in opts:
            if opt in ('--subjectID'):
                subjectID=arg
            elif opt in ('--sessionID'):
                sessionID=arg
            elif opt in ('--bold'):
                bold=arg
            elif opt in ('--structural'):
                structural=arg
            elif opt in ('--card'):
                card=arg
            elif opt in ('--resp'):
                resp=arg
            elif opt in ('--opath'):
                opath=arg
            elif opt in ('--sequence'):
                sequence=arg
            elif opt in ('--connseed'):
                connseed=arg
            elif opt in ('--motpar'):
                motpar=arg
            elif opt in ('--brainmask'):
                brainmask=arg
            elif opt in ('--motglm'):
                motglm=arg
            elif opt in ('--siemensphysio'):
                siemensphysio=arg
            elif opt in ('--biopacphysio'):
                biopacphysio=arg
            elif opt in ('--slicetiming'):
                slicetiming=arg
            elif opt in ('--sliceorder'):
                sliceorder=arg
            elif opt in ('--aseg'):
                aseg=arg
            elif opt in ('--wmseg'):
                wmseg=arg
            elif opt in ('--regintermed'):
                regintermed=arg
        data=Data()
        data.bold=bold
        data.structural=structural
        data.card=card
        data.resp=resp
        data.opath=opath
        data.connseed=connseed
        data.motpar=motpar
        data.brainmask=brainmask
        data.motglm=motglm
        data.siemensphysio=siemensphysio
        data.biopacphysio=biopacphysio
        data.slicetiming=slicetiming
        data.sliceorder=sliceorder
        data.aseg=aseg
        data.wmseg=wmseg
        data.regintermed=regintermed
        run=Run(sequence,data)
        matchsubj=[s for s in subjects if s.ID==subjectID]
        if len(matchsubj)>0:
            subject=matchsubj[0]
        else:
            subject=Subject(subjectID)
            subjects.append(subject)
        matchsess=[s for s in subject.sessions if s.ID==sessionID]
        if len(matchsess)>0:
            session=matchsess[0]
        else:
            session=Session(sessionID)
        session.addrun(run)
        subject.addsession(session)
        line=f.readline()
        l=shlex.split(line)
    return(subjects)

def savesubjects(filename,subjects):
    f=open(filename, 'w')
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                f.write('--subjectID \''+subj.ID+'\' '+\
                        '--sessionID \''+sess.ID+'\' '+\
                        '--sequence \''+run.seqname+'\' '+\
                        '--bold \''+run.data.bold+'\' '+\
                        '--structural \''+run.data.structural+'\' '+\
                        '--card \''+run.data.card+'\' '+\
                        '--resp \''+run.data.resp+'\' '+\
                        '--opath \''+run.data.opath+'\' '+\
                        '--connseed \''+run.data.connseed+'\' '+\
                        '--motpar \''+run.data.motpar+'\' '+\
                        '--brainmask \''+run.data.brainmask+'\' '+\
                        '--motglm \''+run.data.motglm+'\' '+\
                        '--siemensphysio \''+run.data.siemensphysio+'\' '+\
                        '--biopacphysio \''+run.data.biopacphysio+'\' '+\
                        '--slicetiming \''+run.data.slicetiming+'\' '+\
                        '--sliceorder \''+run.data.sliceorder+'\' '+\
                        '--aseg \''+run.data.aseg+'\' '+\
                        '--wmseg \''+run.data.wmseg+'\' '+\
                        '--regintermed \''+run.data.regintermed+'\' '+\
                        '\n')
    f.close()
    

                        
