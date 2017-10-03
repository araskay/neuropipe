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
        #self.tostruct=''
        self.tomni152=''
        self.sliceorder=''
        self.slicetiming=''
        self.structuralcsfpve=''
        self.structuralgmpve=''
        self.structuralwmpve=''
        self.structuralcsfseg=''
        self.structuralgmseg=''
        self.structuralwmseg=''
        self.boldcsfpve=''
        self.boldgmpve=''
        self.boldwmpve=''
        self.boldcsfseg=''
        self.boldgmseg=''
        self.boldwmseg=''
        self.boldcsf=''
        self.boldgm=''
        self.boldwm=''        
        self.func2struct=''
        self.struct2func=''
        self.meantscsf=''
        self.meantsgm=''
        self.meantswm=''
        self.meantsnet=''
        self.imeantscsf=''
        self.imeantsgm=''
        self.imeantswm=''
        self.imeantsnet=''
        
    def parcellate_mprage(self):
        if self.structural == '':
            sys.exity('In parcellate_mprage: Structural data not given. Cannot proceed without. Exiting!')            
        p=subprocess.Popen(['fast','-t','1','-n','3','--segments',\
                            '-o',fileutils.removext(self.structural),\
                            self.structural])
        p.communicate()
        self.structuralcsfpve=fileutils.removext(self.structural)+'_pve_0.nii.gz'
        self.structuralgmpve=fileutils.removext(self.structural)+'_pve_1.nii.gz'
        self.structuralwmpve=fileutils.removext(self.structural)+'_pve_2.nii.gz'
        self.structuralcsfseg=fileutils.removext(self.structural)+'_seg_0.nii.gz'
        self.structuralgmseg=fileutils.removext(self.structural)+'_seg_1.nii.gz'
        self.structuralwmseg=fileutils.removext(self.structural)+'_seg_2.nii.gz'         

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
        '''self.subject1=None
        self.session1=None
        self.run1=None
        self.subject2=None
        self.session2=None
        self.run2=None
        self.metric=None'''
    
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
        '''self.betweensubjectreproducibility=[]
        self.averagebetweensubjectreproducibility=None'''
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
                            
                            if run1.optimalpipeline_r.seedconnoutput=='':
                                run1.optimalpipeline_r.calcseedconn(pthresh)
                            if run1.optimalpipeline_r.seedconnoutputmni152=='':
                                run1.optimalpipeline_r.seedconn2mni()
                            if run2.optimalpipeline_r.seedconnoutput=='':
                                run2.optimalpipeline_r.calcseedconn(pthresh)
                            if run2.optimalpipeline_r.seedconnoutputmni152=='':
                                run2.optimalpipeline_r.seedconn2mni()
                            r_r=spmsim.pearsoncorr(run1.optimalpipeline_r.seedconnoutputmni152,\
                                                   run2.optimalpipeline_r.seedconnoutputmni152)
                            jind_r=spmsim.jaccardind(run1.optimalpipeline_r.seedconn_threshoutputmni152,\
                                                     run2.optimalpipeline_r.seedconn_threshoutputmni152)

                            if run1.optimalpipeline_j.seedconnoutput=='':
                                run1.optimalpipeline_j.calcseedconn(pthresh)
                            if run1.optimalpipeline_j.seedconnoutputmni152=='':
                                run1.optimalpipeline_j.seedconn2mni()
                            if run2.optimalpipeline_j.seedconnoutput=='':
                                run2.optimalpipeline_j.calcseedconn(pthresh)
                            if run2.optimalpipeline_j.seedconnoutputmni152=='':
                                run2.optimalpipeline_j.seedconn2mni()
                            r_j=spmsim.pearsoncorr(run1.optimalpipeline_j.seedconnoutputmni152,\
                                                   run2.optimalpipeline_j.seedconnoutputmni152)
                            jind_j=spmsim.jaccardind(run1.optimalpipeline_j.seedconn_threshoutputmni152,\
                                                     run2.optimalpipeline_j.seedconn_threshoutputmni152)

                            if run1.optimalpipeline_rj.seedconnoutput=='':
                                run1.optimalpipeline_rj.calcseedconn(pthresh)
                            if run1.optimalpipeline_rj.seedconnoutputmni152=='':
                                run1.optimalpipeline_rj.seedconn2mni()
                            if run2.optimalpipeline_rj.seedconnoutput=='':
                                run2.optimalpipeline_rj.calcseedconn(pthresh)
                            if run2.optimalpipeline_rj.seedconnoutputmni152=='':
                                run2.optimalpipeline_rj.seedconn2mni()
                            r_rj=spmsim.pearsoncorr(run1.optimalpipeline_rj.seedconnoutputmni152,\
                                                    run2.optimalpipeline_rj.seedconnoutputmni152)
                            jind_rj=spmsim.jaccardind(run1.optimalpipeline_rj.seedconn_threshoutputmni152,\
                                                      run2.optimalpipeline_rj.seedconn_threshoutputmni152)
                                                      
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
                            
                            '''betsubj=BetweenSubject()
                            betsubj.subject1=subj1
                            betsubj.subject2=subj2
                            betsubj.session1=sess1
                            betsubj.session2=sess2
                            betsubj.run1=run1
                            betsubj.run2=run2
                            betsubj.metric=r
                            self.betweensubjectreproducibility.append(betsubj)
                            avgr=avgr+r
        if count>0:
            avgr=avgr/count
        self.averagebetweensubjectreproducibility=avgr'''
  
        
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
        
        '''for betsubj in self.betweensubjectreproducibility:

            print(betsubj.subject1.ID,'_',betsubj.session1.ID, \
                  'Optimal pipeline:',betsubj.run1.optimalpipeline.getsteps(), \
                  'S-H Reproducibility:',betsubj.run1.optimalpipeline.splithalfseedconnreproducibility)
            print(betsubj.subject2.ID,'_',betsubj.session2.ID, \
                  'Optimal pipeline:',betsubj.run2.optimalpipeline.getsteps(), \
                  'S-H Reproducibility:',betsubj.run2.optimalpipeline.splithalfseedconnreproducibility)
            print('Between subject reproducibility: ',betsubj.subject1.ID,'&',betsubj.subject2.ID,': ',betsubj.metric)
        print('Avg between subj reproducibility: ',self.averagebetweensubjectreproducibility)'''  
        
        
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

# this is to be moved to and intergrated into makeconnseed.py                
def makeconnseed(data,seedatlasfile,atlasfile,ofile,binary):
    # data is a Data object
    # seedatlasfile contains a probabilistic seed ROI on MNI space (e.g., data/atlas/harvard-oxford_cortical_subcortical_structural/pcc.nii.gz)
    img=nibabel.load(data.bold)
    nvol=img.shape[3]
    refvol=nvol/2 # use the middle volume as reference
    # extract brain mask from a temporal mean volume and apply to 4D data
    obase=data.opath
    p=subprocess.Popen(['fslmaths',data.bold,'-Tmean',obase+'__tmean']) # temporal mean
    p.communicate()
    p=subprocess.Popen(['bet2',obase+'__tmean',obase+'__tmean','-f','0.3','-n','-m']) # create a binary mask from the the mean image. (bet2 automatically adds a _mask suffix to the output file)
    p.communicate()
    p=subprocess.Popen(['fslmaths',data.bold,'-mas',obase+'__tmean_mask',obase+'__bet']) # use the mask to brain extract the 4D functional data
    p.communicate()
    # calculate registration parameters
    p=subprocess.Popen(['fslroi',obase+'__bet',obase+'__bet_refvol',str(refvol),'1']) # use the middle volume as reference
    p.communicate()
    p=subprocess.Popen(['flirt','-in',data.bold,'-ref',data.structural,\
                        '-out',fileutils.removext(data.bold)+'__func2struct',\
                        '-omat',fileutils.removext(data.bold)+'__func2struct.mat'])
    p.communicate()
    p=subprocess.Popen(['flirt', '-ref', atlasfile, '-in', data.structural,\
                        '-out', fileutils.removext(data.structural)+'__struct2mni',\
                        '-omat', fileutils.removext(data.structural)+'__struct2mni.mat'])
    p.communicate()
    p=subprocess.Popen(['convert_xfm', '-omat', fileutils.removext(data.bold)+'__func2mni.mat',\
                        '-concat', fileutils.removext(data.structural)+'__struct2mni.mat',\
                        fileutils.removext(data.bold)+'__func2struct.mat'])
    p.communicate()
    p=subprocess.Popen(['convert_xfm', '-inverse', '-omat', fileutils.removext(data.bold)+'__mni2func.mat',\
                        fileutils.removext(data.bold)+'__func2mni.mat'])
    p.communicate()
    # now use the transformation matrix to transfrom the atlas to subject-specific functional space
    p=subprocess.Popen(['flirt', '-in', seedatlasfile,\
                        '-applyxfm', '-init', fileutils.removext(data.bold)+'__mni2func.mat',\
                        '-out', ofile,\
                        '-paddingsize', '0.0', '-interp', 'trilinear', '-ref', data.bold])
    p.communicate()
    if not binary:
        # threshold at 50% and binarize
        p=subprocess.Popen(['fslmaths', ofile, '-thr', '50', '-bin', ofile])
        p.communicate()
    # remove temp files
    return(fileutils.addniigzext(ofile)) # also return the path to the seed file

'''# this is to be moved to and intergrated into makeconnseed.py                
def makeconnseed(data,seedatlasfile,atlasfile,ofile,binary):
    # data is a Data object
    # seedatlasfile contains a probabilistic seed ROI on MNI space (e.g., data/atlas/harvard-oxford_cortical_subcortical_structural/pcc.nii.gz)
    img=nibabel.load(data.bold)
    nvol=img.shape[3]
    refvol=nvol/2 # use the middle volume as reference
    # extract brain mask from a temporal mean volume and apply to 4D data
    obase=data.opath
    p=subprocess.Popen(['fslmaths',data.bold,'-Tmean',obase+'__tmean']) # temporal mean
    p.communicate()
    p=subprocess.Popen(['bet2',obase+'__tmean',obase+'__tmean','-f','0.3','-n','-m']) # create a binary mask from the the mean image. (bet2 automatically adds a _mask suffix to the output file)
    p.communicate()
    p=subprocess.Popen(['fslmaths',data.bold,'-mas',obase+'__tmean_mask',obase+'__bet']) # use the mask to brain extract the 4D functional data
    p.communicate()
    # calculate registration parameters
    p=subprocess.Popen(['fslroi',obase+'__bet',obase+'__bet_refvol',str(refvol),'1']) # use the middle volume as reference
    p.communicate()
    p=subprocess.Popen(['flirt','-in',obase+'__bet_refvol','-ref',data.structural,\
                        '-out',obase+'__func2struct','-omat',obase+'__func2struct.mat', '-dof','7'])
    p.communicate()
    p=subprocess.Popen(['flirt', '-ref', atlasfile, '-in', data.structural,\
                        '-out', obase+'__struct2mni', '-omat', obase+'__struct2mni.mat', '-dof', '12'])
    p.communicate()
    p=subprocess.Popen(['convert_xfm', '-omat', obase+'__func2mni.mat',\
                        '-concat', obase+'__struct2mni.mat', obase+'__func2struct.mat'])
    p.communicate()
    p=subprocess.Popen(['convert_xfm', '-inverse', '-omat', obase+'__mni2func.mat', obase+'__func2mni.mat'])
    p.communicate()
    # now use the transformation matrix to transfrom the atlas to subject-specific functional space
    p=subprocess.Popen(['flirt', '-in', seedatlasfile,\
                        '-applyxfm', '-init', obase+'__mni2func.mat',\
                        '-out', ofile,\
                        '-paddingsize', '0.0', '-interp', 'trilinear', '-ref', obase+'__bet_refvol'])
    p.communicate()
    if not binary:
        # threshold at 50% and binarize
        p=subprocess.Popen(['fslmaths', ofile, '-thr', '50', '-bin', ofile])
        p.communicate()
    # remove temp files
    os.remove(fileutils.addniigzext(obase+'__tmean'))
    os.remove(fileutils.addniigzext(obase+'__tmean_mask'))
    os.remove(fileutils.addniigzext(obase+'__bet'))
    os.remove(fileutils.addniigzext(obase+'__bet_refvol'))
    os.remove(fileutils.addniigzext(obase+'__func2struct'))   
    os.remove(obase+'__func2struct.mat')
    os.remove(fileutils.addniigzext(obase+'__struct2mni'))
    os.remove(obase+'__struct2mni.mat')
    os.remove(obase+'__func2mni.mat')
    os.remove(obase+'__mni2func.mat')
    return(fileutils.addniigzext(ofile)) # also return the path to the seed file'''

'''def skullstrip_fsl(ifile,obase):
    p=subprocess.Popen(['fslreorient2std',ifile,fileutils.removeniftiext(obase)+'_reorient'])
    p.communicate()
    p=subprocess.Popen(['bet',fileutils.removeniftiext(obase)+'_reorient',\
                        fileutils.removeniftiext(obase)+'_reorient_skullstrip'])
    p.communicate()
    return(fileutils.addniigzext(fileutils.removeniftiext(obase)+'_reorient_skullstrip')) # also return the path to the brain extracted file

def skullstrip_afni(ifile,obase):
    p=subprocess.Popen(['fslreorient2std',ifile,fileutils.removeniftiext(obase)+'_reorient'])
    p.communicate()
    p=subprocess.Popen(['3dSkullStrip','-input',fileutils.removeniftiext(obase)+'_reorient.nii.gz',\
                        '-prefix',fileutils.removeniftiext(obase)+'_reorient_skullstrip'])
    p.communicate()
    fileutils.afni2nifti(fileutils.removeniftiext(obase)+'_reorient_skullstrip')
    return(fileutils.addniigzext(fileutils.removeniftiext(obase)+'_reorient_skullstrip')) # also return the path to the brain extracted file'''

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
                        '\n')
    f.close()
    

                        
