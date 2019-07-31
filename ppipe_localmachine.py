#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Use this script to run parallel pipe.py jobs on a machine with multiple cores.
Input arguments are the same as pipe.py with the additional argument --numpar
to set the maximum number of parallel jobs to be run simultaneously.
The input subjects file is split into individual subjects, each of which is run
separately on a separate core.
Report bugs/issues to Aras Kayvanrad (mkayvan@gmail.com).
# (c) Aras Kayvanrad
"""

import sys, os
import subprocess
import distutils.spawn

# check if pipe.py is accessible and if yes,
# add pipe.py directory to path before loading other modules
if distutils.spawn.find_executable('pipe.py') == None:
    print('Cannot find pipe.py. Possible causes/solutions:')
    print('- Make sure the installation directory is added to the path')
    print('- Alternatively you can run directly from the installation directory.')
    sys.exit()
sys.path.insert(distutils.spawn.find_executable('pipe.py'))


import parse
import workflow

parser = parse.ParseArgs(sys.argv[1:], numpar=4)

base_command = 'pipe.py'

count=0
proccount=0
processes = []

for sfile in parser.subjectsfiles:
    subjects=workflow.getsubjects(sfile)
    for s in subjects:
        count+=1
        proccount+=1

        # create the subject file name
        subject_fname = '.temp_subj_'+parser.subjfile+'_'+parser.pipefile+str(count)+'.txt'
        
        command=[]
   
        workflow.savesubjects(subject_fname,[s],append=False)
        
        # create the output and error file names
        outputfile='.temp_job_'+parser.subjfile+'_'+parser.pipefile+str(count)+'.o'
        errorfile='.temp_job_'+parser.subjfile+'_'+parser.pipefile+str(count)+'.e'

        f_o = open(outputfile, 'w')
        f_e = open(errorfile, 'w')
    
        command.append(base_command)

        command = command + parser.replace_subjectsfile(subject_fname)
        
        # now submit job
        print('Running',' '.join(command))
        p=subprocess.Popen(command,stdout=f_o,stderr=f_e)
        processes.append(p)

        if proccount==parser.numpar:
            for p in processes:
                p.wait()
            proccount=0
            processes=[]
            print('Total of',count,'jobs done')

for p in processes:
    p.wait()            
print('Total of',count,'jobs done')
