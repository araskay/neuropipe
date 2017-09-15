import workflow, getopt,sys,fileutils

ifile=''
ofile=''

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:',\
                                ['help','input=', 'output='])
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

if ifile=='' or ofile=='':
    sys.exit('Please provide both input subject file and output subject file')
        
subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            run.data.structural=workflow.skullstrip_fsl(run.data.structural,\
                                                        fileutils.removext(run.data.structural))
            
workflow.savesubjects(ofile,subjects)