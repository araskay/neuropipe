import sys
import spmsim
import fileutils
import getopt,shlex
import os,subprocess,nibabel

class Data:
    def __init__(self):
        self.bold=''
        self.structural=''
        self.card=''
        self.resp=''
        self.opath=''
        self.connseed=''

class BetweenSubject:
    def __init__(self):
        self.subject1=None
        self.session1=None
        self.run1=None
        self.subject2=None
        self.session2=None
        self.run2=None
        self.metric=None
    
class Run:
    def __init__(self,seqname,data):
        self.seqname=seqname
        self.data=data
        self.pipelines=[]
        self.optimalpipeline=None
        
    def setpipelines(self,pipelines):
        self.pipelines=pipelines
    
    def addpipeline(self,pipeline):
        self.pipelines.append(pipeline)
        
    def process(self):
        if (self.pipelines == []):
            sys.exit('Error: No pipelines set for the run. Set pipelines before calling process()')
        for pipe in self.pipelines:
            pipe.run()
      
    def findoptimalpipeline(self):
        if (self.pipelines == []):
            sys.exit('Error: No pipelines set for the run. Set pipelines before calling findoptimalpipeline()')
        self.optimalpipeline=self.pipelines[0]
        for pipe in self.pipelines:
            pipe.calcsplithalfseedconnreproducibility()
            if (1-abs(pipe.splithalfseedconnreproducibility)) < (1-abs(self.optimalpipeline.splithalfseedconnreproducibility)):
                self.optimalpipeline=pipe
 
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
        self.betweensubjectreproducibility=[]
        self.averagebetweensubjectreproducibility=None
      
    def addsubject(self,subject):
        self.subjects.append(subject)
    
    def process(self):
        if (self.subjects == []):
            sys.exit('Error: no subjects to process')
        for subj in self.subjects:
            for sess in subj.sessions:
                for run in sess.runs:
                    run.process()
                    
        
    def findoptimalpipelines(self):
        if (self.subjects == []):
            sys.exit('Error: no subjects to process')
        for subj in self.subjects:
            for sess in subj.sessions:
                for run in sess.runs:
                    run.findoptimalpipeline()
        self.optimalpipelinesfound=True
        
    def computebetweensubjectreproducibility(self,seqName):
        # compute average between subject reproducibility for the given sessionID and seqName
        if not self.optimalpipelinesfound:
            self.findoptimalpipelines()
        count=0
        avgr=0
        for i in range(0,len(self.subjects)):
            for j in range(i+1,len(self.subjects)):
                subj1=self.subjects[i]
                subj2=self.subjects[j]
                for sess1 in subj1.sessions:
                    for sess2 in subj2.sessions:
                        # find the runs that match seqName
                        run1=[r for r in sess1.runs if r.seqname==seqName]
                        run2=[r for r in sess2.runs if r.seqname==seqName]
                        if len(run1)>0 and len(run2)>0:
                            count = count + 1
                            run1=run1[0] # assume there is only one run that matches
                            run1.optimalpipeline.calcseedconn()                            
                            run2=run2[0] # same here
                            run2.optimalpipeline.calcseedconn()
                            r=spmsim.pearsoncorr(fileutils.addniigzext(run1.optimalpipeline.seedconnoutput), \
                                                 fileutils.addniigzext(run2.optimalpipeline.seedconnoutput))
                            # save the result as a BetweenSubject struct
                            betsubj=BetweenSubject()
                            betsubj.subject1=subj1
                            betsubj.subject2=subj2
                            betsubj.session1=sess1
                            betsubj.session2=sess2
                            betsubj.run1=run1
                            betsubj.run2=run2
                            betsubj.metric=r
                            self.betweensubjectreproducibility.append(betsubj)
                            avgr=avgr+r
        avgr=avgr/count
        self.averagebetweensubjectreproducibility=avgr
                
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
        try:
            (opts,args) = getopt.getopt(l,'',['subjectID=',\
                                              'sessionID=',\
                                              'bold=',\
                                              'structural=',\
                                              'card=',\
                                              'resp=',\
                                              'opath=',\
                                              'sequence=',\
                                              'connseed='])
        except getopt.GetoptError:
            sys.exit('Error in subjects file format. Please check the option identifiers in the subjects file (e.g., subjects.txt). Valid identifiers are the following:\n--subjectID\n--sessionID\n--bold\n--structural\n--card\n--resp\n--opath\n--sequence\n--connseed\nAlso please note that identifiers require double dash (--)')
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
        data=Data()
        data.bold=bold
        data.structural=structural
        data.card=card
        data.resp=resp
        data.opath=opath
        data.connseed=connseed
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

                
def makeconnseed(data,seedatlasfile,atlasfile,ofile):
    # data is a Data object
    # seedatlasfile contains a probabilistic seed ROI on MNI space (e.g., data/atlas/harvard-oxford_cortical_subcortical_structural/pcc.nii.gz)
    img=nibabel.load(data.bold)
    nvol=img.shape[3]
    refvol=nvol/2 # use the middle volume as reference
    # extract brain mask from a temporal mean volume and apply to 4D data
    (ipath,ifilename)=os.path.split(data.bold)
    obase=os.path.abspath(data.opath)+'/'+fileutils.removeniftiext(ifilename)
    p=subprocess.Popen(['fslmaths',data.bold,'-Tmean',obase+'_temp_tmean']) # temporal mean
    p.communicate()
    p=subprocess.Popen(['bet2',obase+'_temp_tmean',obase+'_temp_tmean','-f','0.3','-n','-m']) # create a binary mask from the the mean image. (bet2 automatically adds a _mask suffix to the output file)
    p.communicate()
    p=subprocess.Popen(['fslmaths',data.bold,'-mas',obase+'_temp_tmean_mask',obase+'_temp_bet']) # use the mask to brain extract the 4D functional data
    p.communicate()
    # calculate registration parameters
    p=subprocess.Popen(['fslroi',obase+'_temp_bet',obase+'_temp_bet_refvol',str(refvol),'1']) # use the middle volume as reference
    p.communicate()
    p=subprocess.Popen(['flirt','-in',obase+'_temp_bet_refvol','-ref',data.structural,\
                        '-out',obase+'_temp_func2struct','-omat',obase+'_temp_func2struct.mat', '-dof','7'])
    p.communicate()
    p=subprocess.Popen(['flirt', '-ref', atlasfile, '-in', data.structural,\
                        '-out', obase+'_temp_struct2mni', '-omat', obase+'_temp_struct2mni.mat', '-dof', '12'])
    p.communicate()
    p=subprocess.Popen(['convert_xfm', '-omat', obase+'_temp_func2mni.mat',\
                        '-concat', obase+'_temp_struct2mni.mat', obase+'_temp_func2struct.mat'])
    p.communicate()
    p=subprocess.Popen(['convert_xfm', '-inverse', '-omat', obase+'_temp_mni2func.mat', obase+'_temp_func2mni.mat'])
    p.communicate()
    # now use the transformation matrix to transfrom the atlas to subject-specific functional space
    p=subprocess.Popen(['flirt', '-in', seedatlasfile,\
                        '-applyxfm', '-init', obase+'_temp_mni2func.mat',\
                        '-out', ofile,\
                        '-paddingsize', '0.0', '-interp', 'trilinear', '-ref', obase+'_temp_bet_refvol'])
    p.communicate()
    # threshold at 50% and binarize
    p=subprocess.Popen(['fslmaths', ofile, '-thr', '50', '-bin', ofile])
    p.communicate()
    # remove temp files
    os.remove(fileutils.addniigzext(obase+'_temp_tmean'))
    os.remove(fileutils.addniigzext(obase+'_temp_tmean_mask'))
    os.remove(fileutils.addniigzext(obase+'_temp_bet'))
    os.remove(fileutils.addniigzext(obase+'_temp_bet_refvol'))
    os.remove(fileutils.addniigzext(obase+'_temp_func2struct'))   
    os.remove(obase+'_temp_func2struct.mat')
    os.remove(fileutils.addniigzext(obase+'_temp_struct2mni'))
    os.remove(obase+'_temp_struct2mni.mat')
    os.remove(obase+'_temp_func2mni.mat')
    os.remove(obase+'_temp_mni2func.mat')
    return(fileutils.addniigzext(ofile)) # also return the path to the seed file

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
                        '--connseed \''+run.data.connseed+'\''+'\n')
    f.close()
    
                        