#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 16:46:24 2018

@author: mkayvanrad
"""

import subprocess
import pandas as pd
import numpy as np
import getopt,sys

def printhelp():
    print('usage: makeseed.py --locs <csv file> --radius <radius> --template <template file>')
    
locsfile=''
template=''
radius=''


# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','locs=', 'radius=','template='])
except getopt.GetoptError:
    printhelp()
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        printhelp()
        sys.exit()
    elif opt in ('--locs'):
        locsfile=arg
    elif opt in ('--radius'):
        radius=arg
    elif opt in ('--template'):
        template=arg

if locsfile=='' or radius=='' or template=='':
        printhelp()
        sys.exit()
        
        
locs=pd.read_csv(locsfile)

for i in np.arange(len(locs)):
    p=subprocess.Popen(['fslmaths',template,'-mul','0','-add','1','-roi',str(locs.loc[i][1]),'1',str(locs.loc[i][2]),'1',str(locs.loc[i][3]),'1','0','1',locs.loc[i][0],'-odt','float'])
    p.communicate()
    p=subprocess.Popen(['fslmaths',locs.loc[i][0],'-kernel','sphere',radius,'-dilF',locs.loc[i][0]])
    p.communicate()