import workflow
import getopt, sys
import preprocessingstep

class ParseArgs:
    def __init__(self, args=None):
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

        if args is not None:
            self.parse(args)

    def printhelp(self):
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
        print('Report bugs/issues to Aras Kayvanrad (mkayvan@gmail.com)')


    def parse(self, args):
        '''
        Parse command-line arguments
        '''
        try:
            (opts,_) = getopt.getopt(args,'h',\
                                        ['help','pipeline=', 'subjects=',
                                        'showpipe', 'parcellate', 'meants',
                                        'seedconn', 'tomni', 'template=',
                                        'boldregdof=', 'structregdof=',
                                        'boldregcost=', 'structregcost=',
                                        'outputsubjects=', 'keepintermed',
                                        'runpipename=', 'showsubjects',
                                        'maskthresh=', 'opath='])
        except getopt.GetoptError:
            self.printhelp()
            sys.exit()
        for (opt,arg) in opts:
            if opt in ('-h', '--help'):
                self.printhelp()
                sys.exit()
            elif opt in ('--pipeline'):
                self.runpipesteps+=preprocessingstep.makesteps(arg)
                self.runpipe=True
            elif opt in ('--subjects'):
                self.subjectsfiles.append(arg)
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
