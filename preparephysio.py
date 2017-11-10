# this code gets a subject file and runs prepphysio and respbiopac2resp1d.m on the subjects.

import workflow, getopt,sys,fileutils, subprocess,os

def printhelp():
    print('usage: prepaerphysio.py --input <input subject file> --output <output subject file>\n<input subject file needs to contain Siemens and Biopac files.')

ifile=''
ofile=''

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:',\
                                ['help','input=', 'output='])
except getopt.GetoptError:
    printhelp()
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        printhelp()
        sys.exit()
    elif opt in ('-i','--input'):
        ifile=arg
    elif opt in ('-o','--output'):
        ofile=arg

if ifile=='' or ofile=='':
    printhelp()
    sys.exit()
        
subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            p=subprocess.Popen(['prepphysio',run.data.siemensphysio])
            p.communicate()
            (directory,namebase)=os.path.split(run.data.siemensphysio)
            os.rename(namebase+'.resp.1D',directory+'/'+namebase+'.resp.1D')
            os.rename(namebase+'.puls.1D',directory+'/'+namebase+'.puls.1D')
            run.data.card=directory+'/'+namebase+'.puls.1D'
            
            (d,n)=os.path.split(run.data.biopacphysio)
            p=subprocess.Popen(['matlab', \
                                '-nodisplay','-nosplash', '-r',\
                                'respbiopac2resp1d('+'\''+run.data.biopacphysio+'\','+ \
                                '\''+d+'/'+fileutils.removext(n)+'.resp.1D'+'\'); '+ \
                                      'quit;'])
            p.communicate()
            run.data.resp=d+'/'+fileutils.removext(n)+'.resp.1D'
            
workflow.savesubjects(ofile,subjects)
