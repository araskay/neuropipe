import workflow, getopt,sys

ifile=''
ofile=''

seedatlasfile='/home/mkayvanrad/data/atlas/harvard-oxford_cortical_subcortical_structural/pcc.nii.gz'
atlasfile='/usr/share/data/fsl-mni152-templates/MNI152lin_T1_2mm_brain'

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
            run.data.connseed=workflow.makeconnseed(run.data,seedatlasfile,atlasfile,run.data.opath+'_pcc_harvard-oxford')
            
workflow.savesubjects(ofile,subjects)