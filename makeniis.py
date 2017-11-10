# This code reads dicoms from the main dicom folder on chegs (chen_lab/data/dcm), unzips and copies them to <subject>/<session>/dcm folder, and creates nii files in <subject>/<session>/dcm folder. 

import fileutils
import sys, getopt, os
import subprocess

# dictionary of corresponding sessions for Healthy elderly data set
# sessions.keys() gives you all subject IDs
# multiple sessions per subject are added to the lists on the right
sessions=dict()

# healthy volunteer
sessions['7130']=['20140312']
sessions['7934']=['20140207']
sessions['9910']=['20140204']
sessions['10577']=['20140325']
sessions['10649']=['20140316']
sessions['11164']=['20140316']
sessions['11308']=['20140304']
sessions['11494']=['20140311']
sessions['11515']=['20140305']
sessions['11570']=['20140310']
sessions['11672']=['20140318']

# healthy elderly
'''#sessions['11912']=['20170201'] # pilot
#sessions['7397']=['20170213'] # pilot
#sessions['6051']=['20170222'] # pilot
sessions['13719']=['20170316']
sessions['4592']=['20170328']
sessions['10306']=['20170329']
sessions['8971']=['20170413']
sessions['12087']=['20170421']
sessions['12475']=['20170501']
sessions['10724']=['20170526']
sessions['7334']=['20170605']
sessions['14804']=['20170608']
sessions['7982']=['20170612']
sessions['12420']=['20170615']
sessions['8060']=['20170628']'''



baseipath='/data/klymene/chen_lab/data/dcm'
baseopath='/data/klymene/chen_lab/mkayvanrad/data/healthyvolunteer'

baseipath=os.path.abspath(baseipath) # just to remove possible end slash (/) for consistency
baseopath=os.path.abspath(baseopath) # same here
for subj in sessions.keys():
    for sess in sessions[subj]:
        dcmfolder=baseopath+'/'+subj+'/'+sess+'/'+'dcm'
        niifolder=baseopath+'/'+subj+'/'+sess+'/'+'nii'
        # unzip dicom files
        fileutils.createdir(dcmfolder)
        p=subprocess.Popen(['unzip','-o','-d',dcmfolder,baseipath+'/'+subj+'_'+sess+'/*.zip'])
        p.communicate()
        # convert to nii
        fileutils.createdir(niifolder)
        p=subprocess.Popen(['dcm2nii','-4','-g','-a','n','-d','n','-e','n','-p','y','-i','n',\
                            '-o',niifolder,dcmfolder])
        p.communicate()        
