import workflow, getopt,sys,os,fileutils,subprocess,pipeline,copy,preprocessingstep

def printhelp():
    print('usage: makeconnseed.py --input <input subject file> --output <output subject file> --seed <seed file> --template <template file> [--binary[=FALSE] --boldregdof <dof> --structregdof <dof> --boldregcost <cost func> --structregcost <cost func>]\n<seed file> must be in the same space as the <template file> (e.g., both in MNI). Unless --binary used, by default the code assumes a probabilistic seed file with percentage values (i.e., 0< and <100).')

ifile=''
ofile=''
seedatlasfile=''
binary=False

envvars=workflow.EnvVars()

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:s:t:',\
                                ['help','input=', 'output=', 'seed=' , 'template=', 'binary','boldregdof=','structregdof=','boldregcost=','structregcost='])
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
    elif opt in ('-s','--seed'):
        seedatlasfile=arg
    elif opt in ('-t','--template'):
        envvars.mni152=arg
    elif opt in ('--binary'):
        binary=True
    elif opt in ('--boldregdof'):
        envvars.boldregdof=arg
    elif opt in ('--structregdof'):
        envvars.structregdof=arg
    elif opt in ('--boldregcost'):
        envvars.boldregcost=arg
    elif opt in ('--structregcost'):
        envvars.structregcost=arg

if ifile=='' or ofile=='' or seedatlasfile=='' or envvars.mni152=='':
    printhelp()
    sys.exit()
        
subjects=workflow.getsubjects(ifile)

(directory,namebase)=os.path.split(seedatlasfile)
namebase=fileutils.removext(namebase)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            if run.data.mni2func=='':
                data=copy.deepcopy(run.data)
                data.envvars=envvars
                # first do motion correction (to make tmean, based on which registration parameters are found, more accurate)
                mcflirt=preprocessingstep.PreprocessingStep('mcflirt',[])
                pipe=pipeline.Pipeline('',[mcflirt])
                pipe.setibase(data.bold)
                pipe.setobase(data.opath)
                pipe.setdata(data)
                pipe.run()
                # now find registration parameters
                data.bold=pipe.output
                data.transform_mni2func()
                
                run.data.func2struct=data.func2struct
                run.data.struct2func=data.struct2func
                run.data.struct2mni=data.struct2mni
                run.data.mni2struct=data.mni2struct
                run.data.func2mni=data.func2mni
                run.data.mni2func=data.mni2func
                

            # now use the transformation matrix to transfrom the atlas to subject-specific functional space
            p=subprocess.Popen(['flirt', '-in', seedatlasfile,\
                                '-applyxfm', '-init', run.data.mni2func,\
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
