import workflow, getopt,sys,fileutils,shutil,os, subprocess

ifile=''
ofile=''
skiprecon=False

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:',\
                                ['help','input=', 'output=', 'skiprecon'])
except getopt.GetoptError:
    print('usage: makeconnseed.py -i <input subject file> -o <output subject file>')
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        print('usage: makeconnseed.py -i <input subject file> -o <output subject file>')
        sys.exit()
    elif opt in ('-i','--input'):
        ifile=arg
    elif opt in ('-o','--output'):
        ofile=arg
    elif opt in ('--skiprecon'):
        skiprecon=True

if ifile=='' or ofile=='':
    sys.exit('Please provide both input subject file and output subject file')
        
subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            (opath,oname)=os.path.split(run.data.structural)
            fileutils.createdir(opath)
            if not skiprecon:
                p=subprocess.Popen(['recon-all','-sd',opath,'-subjid','__recon-all','-i',run.data.structural,'-autorecon1'])
                p.communicate()
            p=subprocess.Popen(['mri_convert',opath+'/__recon-all/mri/brainmask.mgz',\
                                opath+'/'+fileutils.removext(oname)+'_brainmask.nii.gz'])
            p.communicate()
            run.data.structural=opath+'/'+fileutils.removext(oname)+'_brainmask.nii.gz'
            #shutil.rmtree(opath+'/__recon-all')
            
            
workflow.savesubjects(ofile,subjects)
