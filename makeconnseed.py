import workflow, getopt,sys

ifile=''
ofile=''

seedatlasfile=''
atlasfile=''

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hi:o:s:t:',\
                                ['help','input=', 'output=', 'seed=' , 'template='])
except getopt.GetoptError:
    print('usage: makeconnseed.py -i <input subject file> -o <output subject file> -s <seed file> -t <template file>')
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        print('usage: makeconnseed.py -i <input subject file> -o <output subject file> -s <seed file> -t <template file>')
        sys.exit()
    elif opt in ('-i','--input'):
        ifile=arg
    elif opt in ('-o','--output'):
        ofile=arg
    elif opt in ('-s','--seed'):
        seedatlasfile=arg
    elif opt in ('-t','--template'):
        atlasfile=arg

if ifile=='' or ofile=='' or seedatlasfile=='' or atlasfile=='':
    sys.exit('usage: makeconnseed.py -i <input subject file> -o <output subject file> -s <seed file> -t <template file>')
        
subjects=workflow.getsubjects(ifile)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            run.data.connseed=workflow.makeconnseed(run.data,seedatlasfile,atlasfile,run.data.opath+'_pcc_harvard-oxford')
            
workflow.savesubjects(ofile,subjects)
