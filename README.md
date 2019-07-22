# NeuroPipe
This project aims to create flexible and scalable fMRI preprocessing pipelines. *NeuroPipe* uses an object-oriented framework to create and run preprocessing pipelines. In this framework, each *pipeline* consists of a number of *preprocessing steps*, where each proprocessing step is an object of class *PreprocessingStep*. This design allows to construct versatile pipelines in which different preprocessing steps can be used in any desired order.

## Installation
Clone the repository into a directory of your choice.

```
git clone https://github.com/kayvanrad/fmri_pipeline.git
```

Quick note for beginners: In linux/unix, you can add the installation directory to make pipe.py accessible from any directory. Simply add the following line to *~/.bashrc* or *~/.bash_profile*:
```
export PATH="${PATH}:<path to directory>"
```
where <path to directory> is the path to the installation directory.

## Requirements
### Python version
The pipeline requires python 3 to run. However, if you really want to use python 2, you should be able to get it running in python 2 as well with some modifications. I recommend using [Anaconda Python 3](https://www.anaconda.com).

### Required libraries
Please refer to requirements.txt for a list of the required libraries. The libraries can be installed using pip as follows:
```
pip install --user -r requirements.txt
```

### Required MRI software packages
The pipeline calls *FSL*, *AFNI*, and *Freesurfer* tools for preprocessing. For the pipeline to run properly, you need to have these software packages installed and the pipeline should be able to find them in the PATH.

## GETTING STARTED
pipe.py offers a range of capabilities for preprocessing and analysis of fMRI data. The following provides a quick start guide to the most common application, i.e. running a preprocessing pipeline on a set of data. If you are looking for a pipeline to preprocess your fMRI data this is what you need. For more advanced/detailed functionality see the User Guide. 

### Syntax 
The following runs a preprocessing pipeline on the data for all the subjects listed in the ‘subjects file’.  
```
pipe.py --subjects <subjects file> --pipeline <pipeline file> 
```
<subjects file> is a text file, which lists the path to data files for all the subjects to be preprocessed. The file lists all the required data in a simple format. For a list of all data fields refer to the User Guide. 

<pipeline file> is a text file listing the preprocessing steps to be run as part of the preprocessing pipeline, in a simple format. For a list of the available preprocessing steps refer to the User Guide. 

### Example 
```
pipe.py --subjects mySubjects.txt --pipeline myPipeline.txt 
```

*myPipeline.txt*:
```
slicetimer --odd 
mcflirt 
brainExtractAFNI 
ssmooth -fwhm 5 
3dFourier -highpass 0.01 -ignore 0 
retroicor -ignore 10  
```

*mySubjects.txt*:
```
--bold ‘/data/experiment1/nii/subject1_bold.nii.gz’ --structural ‘/data/experiment1/nii/subject1_struct.nii.gz’ --structuralbrainmask ‘/data/experiment1/nii/subject1_struct_brainmask.nii.gz’ --opath ‘/data/experiment1/processed’ 
--bold ‘/data/experiment1/nii/subject2_bold.nii.gz’ --structural ‘/data/experiment1/nii/subject2_struct.nii.gz’ --structuralbrainmask ‘/data/experiment1/nii/subject2_struct_brainmask.nii.gz’ --opath ‘/data/experiment1/processed’ 
```

### Parallel processing
- on a single machine with multiple cores: ppipe_localmachine.py
- on a high performance computing (HPC) cluster: ppipe_cac.py.

Note: ppipe_cac.py is written for the CAC HPC cluster at Queen's University. The user may wish to make minor modifications to the script as appropriate for other clusters.

Please consult the [user guide](https://github.com/kayvanrad/neuropipe/blob/master/user_guide.pdf) for detailed description of the available tools.

## Getting help 
To get help, type the following in the terminal: 
```
pipe.py --help 
```



