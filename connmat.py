import sys, getopt
import workflow
import numpy as np
from nilearn.input_data import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure


def connectivity_matrix(atlas_filename, fmri_filename, kind = 'correlation'):
    '''
    Calculate functional connectivity matrix.
    Inputs:
        atlas_filename: path / file name of the labels image
        fmri_filename: path / file name of the fMRI image
        kind: connectivity kind, {“correlation”, “partial correlation”, “tangent”, “covariance”, “precision”}, optional
    Output:
        conn_matrix: connectivity matrix, numpy array
    '''

    # calculate time series over each label
    masker = NiftiLabelsMasker(labels_img=atlas_filename, verbose=5)
    time_series = masker.fit_transform(fmri_filename)

    # calculate connectivity matrix
    conn_measure = ConnectivityMeasure(kind='correlation')
    conn_matrix = conn_measure.fit_transform([time_series])[0]

    return conn_matrix

def printhelp():
    print('Usage: connmat.py --subjects <subjects file> --atlas <atlas file> [--kind <connectivity kind {“correlation” (default), “partial correlation”, “tangent”, “covariance”, “precision”}>')
    
subjects_file=''
atlas_file=''
kind='correlation'

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','subjects=', 'atlas=', 'kind='])
except getopt.GetoptError:
    printhelp()
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        printhelp()
        sys.exit()
    elif opt in ('--subjects'):
        subjects_file=arg
    elif opt in ('--atlas'):
        atlas_file=arg
    elif opt in ('--kind'):
        kind=arg

if subjects_file=='' or atlas_file=='':
    printhelp()
    sys.exit()

subjects=workflow.getsubjects(subjects_file)

for subj in subjects:
    for sess in subj.sessions:
        for run in sess.runs:
            connmat = connectivity_matrix(atlas_filename=atlas_file,
                                          fmri_filename=run.data.bold,
                                          kind=kind)
            np.savetxt(run.data.bold+'_connmat.csv',connmat, delimiter=',')
            run.data.connmat = run.data.bold+'_connmat.csv'
                
workflow.savesubjects(subjects_file,subjects,append=False)