import workflow
import getopt, sys, os, copy
import preprocessingstep

class ParseArgs:
    def __init__(self, args, mem=0, numpar=0):
        self.args = args
        self.mem = mem # default memory for parallel processing - ignored if 0
        self.numpar = numpar # default number parallel processes for parallel processing - ignored if 0
        self.subjectsfiles=[]
        self.runpipesteps=[] # this is a list
        self.showpipes=False
        self.parcellate=False
        self.meants=False
        self.seedconn=False
        self.tomni=False
        self.runpipename=''
        self.outputsubjectsfile=''
        self.keepintermed=False
        self.runpipe=False
        self.showsubjects=False
        self.opath=''
        self.envvars=workflow.EnvVars()

        # the following used by parallel processing wrappers (e.g., ppipe_localmachine.py)
        self.pipefile=''
        self.subjfile=''             

        # list of all valid arguments
        self.argslist=['help','pipeline=', 'subjects=',
                        'showpipe', 'parcellate', 'meants',
                        'seedconn', 'tomni', 'template=',
                        'boldregdof=', 'structregdof=',
                        'boldregcost=', 'structregcost=',
                        'outputsubjects=', 'keepintermed',
                        'runpipename=', 'showsubjects',
                        'maskthresh=', 'opath=']
            
        if self.mem>0 or self.numpar>0:
            self.parse_parallel_proc()

        self.parse()
        self.check_args()

    def printhelp(self, extended=False):
        print('USAGE:')
        print(('pipe.py  --subjects <subjects file>'
            ' [--pipeline <pipeline file>]'
            ' [--showpipe]'
            ' [--parcellate]'
            ' [--meants]'
            ' [--seedconn]'
            ' [--tomni]'
            ' [--template <template file>]'
            ' [--resout <base name>]'
            ' [--keepintermed]'
            ' [--boldregdof <dof>]'
            ' [--structregdof <dof>]'
            ' [--boldregcost <cost function>]'
            ' [--structregcost <cost function>]'
            ' [--runpipename <name>]'
            ' [--outputsubjects <subj file>]'
            ' [--showsubjects]'
            ' [--maskthresh]'
            ' [--opath <output path>]'))
        if self.numpar>0 or self.mem>0:
            print('---------------------------------------')
            print('Additional parallel processing options:')
        if self.numpar>0:
            print('[--numpar <number of parallel jobs = 16>]')
        if self.mem>0:
            print('--mem <amount in GB = 16>')
        print('')
        if extended:
            print('ARGUMENTS:')
            print('--subjects <subj file>: specify subjects file (required)')
            print('--pipeline <pipe file>: specify a pipeline file to be run on all subjects without optimization and/or calculation of between subject metrics')
            print('--showpipe: show the pipeline to be run without running. Only use to see a list of pipelines to be run/optimized. This will NOT run/optimize the pipelines. Remove the flag to run/optimize.')
            print('--parcellate: parcellate the output of the run/optimal/fixed pipeline(s).')
            print('--meants: compute mean time series over CSF, GM, and WM for the pipeline output. This automatically parcellates the output. If used with --seedconn, mean time series over the network is also computed.')
            print('--seedconn: compute seed-connectivity network on the pipeline output. Need to provide a seed file in subjects file.')
            print('--tomni: transform pipeline output and seed connectivity (if available) to standard MNI space. Requires template to be specified')
            print('--template <temp file>: template file to be used for between subject calculations, e.g., MNI template.')
            print('--keepintermed: keep results of the intermediate steps')
            print('--boldregdof <dof>: degrees of freedom to be used for bold registration (Default = 12).')
            print('--structregdof <dof>: degrees of freedom to be used for structural registration (Default = 12).')
            print('--boldregcost <cost function>: cost fuction to be used for bold registration (Default = \'corratio\').')
            print('--structregcost <cost function>: cost fuction to be used for structural registration (Default = \'corratio\').')
            print('--runpipename <name>: prefix to precede name of steps in the run pipeline output files. (Default=\'\')')
            print('--outputsubjects <subj file>: specify a subject file, to which the results of the pipeline run on all subjects is appended. Only applicable with --pipeline.')
            print('--showsubjects: print the list of all subjects to be processed and exit.')
            print('--maskthresh: threshold for binarizing functional masks transformed from structural masks (Default=0.5)')
            print('--opath <output path>: output path- overrides the opath in subjects file')
            print('')
            print('Report bugs/issues to Aras Kayvanrad (mkayvan@gmail.com)')
            print('')


    def parse(self):
        '''
        Parse command-line arguments
        '''
        try:
            (opts,_) = getopt.getopt(self.args,'h',self.argslist)
        except getopt.GetoptError:
            self.printhelp()
            sys.exit()
        for (opt,arg) in opts:
            if opt in ('-h', '--help'):
                self.printhelp(extended=True)
                sys.exit()
            elif opt in ('--pipeline'):
                self.runpipesteps+=preprocessingstep.makesteps(arg)
                self.runpipe=True
                # get the name of the pipeline file - used by parallel processing wrappers
                (_,self.pipefile)=os.path.split(arg)
            elif opt in ('--subjects'):
                self.subjectsfiles.append(arg)
                # get the name of the subjects file - used by parallel processing wrappers
                (_,filename)=os.path.split(arg)
                # the program allows multiple subjects files to be given
                self.subjfile=self.subjfile+filename
            elif opt in ('--showpipe'):
                self.showpipes=True
            elif opt in ('--template'):
                self.envvars.mni152=arg
            elif opt in ('--parcellate'):
                self.parcellate=True
            elif opt in ('--meants'):
                self.meants=True
            elif opt in ('--seedconn'):
                self.seedconn=True
            elif opt in ('--tomni'):
                self.tomni=True
            elif opt in ('--boldregdof'):
                self.envvars.boldregdof=arg
            elif opt in ('--structregdof'):
                self.envvars.structregdof=arg
            elif opt in ('--boldregcost'):
                self.envvars.boldregcost=arg
            elif opt in ('--structregcost'):
                self.envvars.structregcost=arg
            elif opt in ('--outputsubjects'):
                self.outputsubjectsfile=arg
            elif opt in ('--keepintermed'):
                self.keepintermed=True
            elif opt in ('--runpipename'):
                self.runpipename=arg
            elif opt in ('--showsubjects'):
                self.showsubjects=True
            elif opt in ('--maskthresh'):
                self.envvars.maskthresh=arg
            elif opt in ('--opath'):
                self.opath=arg

    def check_args(self):
        if not self.isValid():
            self.printhelp()
            sys.exit()

        if self.subjectsfiles==[]:
            self.printhelp()
            sys.exit()

        if self.tomni and self.envvars.mni152=='':
            sys.exit('--tomni used but template not specified. Need to provide --template to use --tomni.')        

    def isValid(self):
        '''
        The getopt libraray somehow "guesses" the arguments - for example if given
        '--subject' it will automatically produce '--subjects'. This can cause problems
        later when arguments from sys.argv are passed to pipe.py. This function checks
        in advance to avoid such problems.
        '''
        valid=True
        for arg in self.args:
            if '--' in arg:
                if not arg in ['--'+x.replace('=', '') for x in self.argslist]:
                    valid=False
        return(valid)

    def parse_parallel_proc(self):
        # check to see if the output subjects file exists and, if it does, add
        # a number to the given file to avoid appending the results to the
        # existing file
        duplicate_count = 0
        if '--outputsubjects' in self.args:
            s = self.args[self.args.index('--outputsubjects')+1]
            while os.path.exists(s):
                duplicate_count += 1
                s = self.args[self.args.index('--outputsubjects')+1] + str(duplicate_count)
            self.args[self.args.index('--outputsubjects')+1] = s

        if self.mem > 0:
            if '--mem' in self.args:
                self.mem = int(self.args[self.args.index('--mem')+1])
                del self.args[self.args.index('--mem')+1]
                del self.args[self.args.index('--mem')]
        if self.numpar > 0:
            if '--numpar' in self.args:
                self.numpar = int(self.args[self.args.index('--numpar')+1])
                del self.args[self.args.index('--numpar')+1]
                del self.args[self.args.index('--numpar')]

    def replace_subjectsfile(self,filename):
        a = copy.deepcopy(self.args)
        a[a.index('--subjects')+1] = filename
        return(a)
