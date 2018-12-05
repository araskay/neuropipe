#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 12:00:23 2018

@author: mkayvanrad
"""

import getopt, os
import fileutils

def argsvalid(args):
    for arg in args:
        if '--' in arg:
            if not arg in ['--help','--pipeline', '--subjects', '--perm', '--onoff',\
                           '--permonoff', '--const', '--select', '--add',\
                           '--combine', '--fixed', '--showpipes', '--template',\
                           '--resout', '--parcellate', '--meants', '--seedconn',\
                           '--tomni', '--boldregdof', '--structregdof',\
                           '--boldregcost', '--structregcost', '--outputsubjects',\
                           '--keepintermed', '--runpipename', '--fixpipename',\
                           '--optpipename','--opath','--mem','--numpar']:
                return(False)
            else:
                return(True)
                

class arguments:
    def __init__(self):
        self.help=False
        self.pipefile=''
        self.subjfile=''
        self.error=False
        self.subjectsfiles=[]
        self.mem='16'
        self.numpar=16

def parseargs(args):
    # parse command-line arguments
    out=arguments()
    try:
        (opts,_) = getopt.getopt(args,'h',\
                                    ['help','pipeline=', 'subjects=', 'perm=',\
                                     'onoff=', 'permonoff=', 'const=', 'select=',\
                                     'add', 'combine', 'fixed=', 'showpipes',\
                                     'template=', 'resout=', 'parcellate',\
                                     'meants', 'seedconn', 'tomni', 'boldregdof=',\
                                     'structregdof=', 'boldregcost=',\
                                     'structregcost=', 'outputsubjects=',\
                                     'keepintermed', 'runpipename=',\
                                     'fixpipename=', 'optpipename=','opath=',\
                                     'mem=','numpar='])
    except getopt.GetoptError:
        out.error=True
        return(out)
    for (opt,arg) in opts:
        if opt in ('-h', '--help'):
            out.help=True
        elif opt in ('--pipeline'):
            (directory,out.pipefile)=os.path.split(arg)
        elif opt in ('--subjects'):
            out.subjectsfiles.append(arg)
            (directory,filename)=os.path.split(arg)
            out.subjfile=out.subjfile+filename
        elif opt in ('--mem'):
            out.mem=arg
        elif opt in ('--numpar'):
            out.numpar=int(arg)
        elif opt in ('--outputsubjects'):
            fileutils.removefile(arg) # if output subjects file exists, delete it
            
    return(out)
    
def getjobargs(pipe_args, subject_fname):
    pipe_args[pipe_args.index('--subjects')+1] = subject_fname
    if '--mem' in pipe_args:
        del pipe_args[pipe_args.index('--mem')+1]
        del pipe_args[pipe_args.index('--mem')]
    if '--numpar' in pipe_args:
        del pipe_args[pipe_args.index('--numpar')+1]
        del pipe_args[pipe_args.index('--numpar')]
    return(pipe_args)