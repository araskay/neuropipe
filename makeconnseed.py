import workflow, getopt,sys,os,fileutils,subprocess

ifile=''
ofile=''
seedatlasfile=''
atlasfile=''
binary=False
boldregdof='12'
structregdof='12'

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:s:t:',\
                                ['help','input=', 'output=', 'seed=' , 'template=', 'binary','boldregdof=','structregdof='])
except getopt.GetoptError:
    print('usage: makeconnseed.py -i <input subject file> -o <output subject file> -s <seed file> -t <template file> [--binary --boldregdof <dof> --structregdof <dof>]')
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        print('usage: makeconnseed.py -i <input subject file> -o <output subject file> -s <seed file> -t <template file> [--binary --boldregdof <dof> --structregdof <dof>]')
        sys.exit()
    elif opt in ('-i','--input'):
        ifile=arg
    elif opt in ('-o','--output'):
        ofile=arg
    elif opt in ('-s','--seed'):
        seedatlasfile=arg
    elif opt in ('-t','--template'):
        atlasfile=arg
    elif opt in ('--binary'):
        binary=True
    elif opt in ('--boldregdof'):
        boldregdof=arg
    elif opt in ('--structregdof'):
        structregdof=arg

if ifile=='' or ofile=='' or seedatlasfile=='' or atlasfile=='':
    sys.exit('usage: makeconnseed.py -i <input subject file> -o <output subject file> -s <seed file> -t <template file>')
        
subjects=workflow.getsubjects(ifile)

(directory,namebase)=os.path.split(seedatlasfile)
namebase=fileutils.removext(namebase)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            # first create mean time series
            p=subprocess.Popen(['fslmaths',run.data.bold,'-Tmean',fileutils.removext(run.data.bold)+'__meants'])
            p.communicate()
            #register mean time series volume to structural
            #run.data.parcellate_structural()

            p=subprocess.Popen(['flirt','-in',fileutils.removext(run.data.bold)+'__meants','-ref',run.data.structural,\
                                '-dof',boldregdof,\
                                '-cost','bbr',\
                                '-bbrtype','global_abs',\
                                '-out',fileutils.removext(run.data.bold)+'__meants_func2struct',\
                                '-omat',fileutils.removext(run.data.bold)+'__func2struct.mat'])
            p.communicate()
            # register structural to standard template
            p=subprocess.Popen(['flirt', '-ref', atlasfile, '-in', run.data.structural,\
                                '-dof',structregdof,\
                                '-out', fileutils.removext(run.data.structural)+'__struct2mni',\
                                '-omat', fileutils.removext(run.data.structural)+'__struct2mni.mat'])
            p.communicate()
            #
            p=subprocess.Popen(['convert_xfm', '-omat', fileutils.removext(run.data.bold)+'__func2mni.mat',\
                                '-concat', fileutils.removext(run.data.structural)+'__struct2mni.mat',\
                                fileutils.removext(run.data.bold)+'__func2struct.mat'])
            p.communicate()
            p=subprocess.Popen(['convert_xfm', '-inverse', '-omat', fileutils.removext(run.data.bold)+'__mni2func.mat',\
                                fileutils.removext(run.data.bold)+'__func2mni.mat'])
            p.communicate()
            # now use the transformation matrix to transfrom the atlas to subject-specific functional space
            p=subprocess.Popen(['flirt', '-in', seedatlasfile,\
                                '-applyxfm', '-init', fileutils.removext(run.data.bold)+'__mni2func.mat',\
                                '-out', fileutils.removext(run.data.bold)+'_'+namebase,\
                                '-ref', run.data.bold])
            p.communicate()
            if not binary:
                # threshold at 50% and binarize
                p=subprocess.Popen(['fslmaths', fileutils.removext(run.data.bold)+'_'+namebase,\
                                    '-thr', '50', '-bin', fileutils.removext(run.data.bold)+'_'+namebase])
                p.communicate()
            else:
                # threshold at 0.5 and binarize
                p=subprocess.Popen(['fslmaths', fileutils.removext(run.data.bold)+'_'+namebase,\
                                    '-bin', fileutils.removext(run.data.bold)+'_'+namebase])
                p.communicate()
                
            run.data.connseed=fileutils.addniigzext(fileutils.removext(run.data.bold)+'_'+namebase)
            
workflow.savesubjects(ofile,subjects)
