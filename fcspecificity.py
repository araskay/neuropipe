# this script computes specificity for FC following Chai et al, Neuroimage 2012. The script gets the following three text files: (1) file containing path/name of FC SPM files (e.g., z-scores) in the standard space for all subjects, (2) file containing list of the seed and all the target ROIs (the first entry is assumed to be the seed and the rest to be target ROIs), and (3) file containing list of all the reference (target) ROIs.

import nibabel,sys
import numpy as np
import scipy.stats
import statsmodels.stats.multitest as mtest
import getopt, os, fileutils

def groupaverage(spmfiles):

    n=len(spmfiles)
    
    # the following just to get the size of the SPMs
    img_nib=nibabel.load(spmfiles[0])
    img=img_nib.get_data()
   
    avg=np.zeros(img.shape)
    for i in np.arange(n):
        spm_nib=nibabel.load(spmfiles[i])
        spm=spm_nib.get_data()
        avg=avg+spm
    
    avg=avg/n

    return(avg)
                


def printhelp():
    print('Usage: fcspecificity --spms <text file> --targetrois <text file> --referencerois <text file> --ofile <text file> [--n=1000 <number of bootstrap iterations> --grpavg <nii file name>]')


n=1000
spmsfile=''
targetroisfile=''
referenceroisfile=''
ofile=''
grpavgfile=''
    
# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','spms=', 'targetrois=','referencerois=', 'ofile=','n=','grpavg='])
except getopt.GetoptError:
    printhelp()
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        printhelp()
        sys.exit()
    elif opt in ('--spms'):
        spmsfile=arg
    elif opt in ('--targetrois'):
        targetroisfile=arg
    elif opt in ('--referencerois'):
        referenceroisfile=arg
    elif opt in ('--ofile'):
        ofile=arg
    elif opt in ('--n'):
        n=float(arg)
    elif opt in ('--grpavg'):
        grpavgfile=arg

#spmsfile='/rri_disks/liberatrix/chen_lab/aras/data/healthyvolunteer/processed/physcor-nomotreg/fepi/motorseed/spmlist_nocor_z.txt'
#targetroisfile='/rri_disks/liberatrix/chen_lab/aras/data/healthyvolunteer/processed/physcor-nomotreg/fepi/motorseed/target_rois.txt'
#referenceroisfile='/rri_disks/liberatrix/chen_lab/aras/data/healthyvolunteer/processed/physcor-nomotreg/fepi/motorseed/ref_rois.txt'
#ofile='/rri_disks/liberatrix/chen_lab/aras/data/healthyvolunteer/processed/physcor-nomotreg/fepi/motorseed/fc_specificity.csv'

if spmsfile=='' or targetroisfile=='' or referenceroisfile=='' or ofile=='':
    printhelp()
    sys.exit()

# read all the FC SPMs into a list

np.random.seed(0)

spms=[]
f=open(spmsfile)
spm=f.readline()
spm=spm.rstrip()
while len(spm)>0:
    spms.append(spm)
    spm=f.readline()
    spm=spm.rstrip()

targetrois=[]
f=open(targetroisfile)
targetroi=f.readline()
targetroi=targetroi.rstrip()
while len(targetroi)>0:
    targetrois.append(targetroi)
    targetroi=f.readline()
    targetroi=targetroi.rstrip()

referencerois=[]
f=open(referenceroisfile)
referenceroi=f.readline()
referenceroi=referenceroi.rstrip()
while len(referenceroi)>0:
    referencerois.append(referenceroi)
    referenceroi=f.readline()
    referenceroi=referenceroi.rstrip()

fout=open(ofile,'w')

for j in np.arange(len(targetrois)):
    (opath,oname)=os.path.split(targetrois[j])
    if j>0:
        fout.write(',')
    fout.write(oname)
fout.write('\n')

ref_nib=nibabel.load(referencerois[0])
ref=ref_nib.get_data()
affine=ref_nib.affine # used to save the result in a NIFTI file
hdr=ref_nib.header # also used to save the result
    

# while here, save the group average
if len(grpavgfile)>0:
    grp=groupaverage(spms)
    onifti = nibabel.nifti1.Nifti1Image(grp,affine,header=hdr)
    onifti.to_filename(grpavgfile)

for i in np.arange(n):
    resamp=np.random.choice(spms,size=len(spms),replace=True)
    grp=groupaverage(resamp)
   
    for j in np.arange(len(targetrois)):
        target_nib=nibabel.load(targetrois[j])
        target=target_nib.get_data()
    
        ztarget=np.mean(grp[np.where(target==1)])
        zref=np.mean(grp[np.where(ref==1)])
       
        s=(abs(ztarget)-abs(zref))/(abs(ztarget)+abs(zref))

        if j>0:
            fout.write(',')
        fout.write(str(s))
    fout.write('\n')
    
fout.close()    

