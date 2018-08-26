.
===========================================================================
     README:  reproducible Canonical Autocorrelation Analysis (2013/07/12)  
===========================================================================
     Author: Nathan Churchill, University of Toronto
      email: nchurchill@research.baycrest.org
===========================================================================

This folder contains scripts for reproducible Canonical Autocorrelations Analysis
(rCAA). It is a modified version of the algorithm which PHYCAA+ is based on,
which can be used to explore autocorrelation structure in your data.
It is a multivariate component decomposition model (similar to ICA or PCA), 
that identifies a set of orthonormal timeseries that are (a) maximally autocorrelated in 
time and (b) highly spatially reproducible. It has both a script for data
in matlab format, of 2D (voxels x time) matrices (rCAA.m), and a wrapper script, that
does component decomposition directly on 4D NIFTI data (run_rCAA.m). See below for details.
Further algorithm details provided in:

  Churchill & Strother (2013). "PHYCAA+: An Optimized, Adaptive
  Procedure for Measuring and Controlling Physiological Noise in BOLD fMRI". NeuroImage 82: 306-325

Please cite this article if code is used in any publications.

%---------------------------------------------------------------------------------------------------
%  RCAA: reproducible Canonical Autocorrelations Analysis (CAA), used to identify a set of 
%  orthonormal timeseries that are (a) maximally autocorrelated in time and (b) highly spatially 
%  reproducible.  This has the extra feature that you can search for components that have central 
%  frequency  in a specific frequency band (see details below).
%---------------------------------------------------------------------------------------------------
%
%  Syntax:
%             outputs = rCAA( dataMatA, dataMatB, TR, offSet, band_select )
%  Inputs:
%
%  dataMatA, dataMatB = fMRI data matrices of size (voxels x time), although #timepoints can vary between splits.
%                       Requires 2 runs to identify reproducible spatial structure in data
%                  TR = acquisition time intervals (in sec.)
%              offSet = autocorrelation lag that is optimized in this model (integer value >0). Recommended
%                       offSet=1 generally works well, unless there is a good reason to choose otherwise
%         band_select = 2D vector, specifying the frequency range (in Hz) where components' central frequency
%                       must be, to select in CAA model. Formatted as "band_select = [Low_threshold High_threshold]"
%                       If you don't want to constrain components by frequency, just set as empty (e.g. band_select=[]).
R
%  Outputs:   
%         outputs = structure with the following elements:
%
%             outputs.rep   : spatial reproducibility of CAA components
%             outputs.SPM   : (voxels x components) matrix of Z-scored, reproducible component spatial maps
%             outputs.TsetA : (time x components) matrix of component timecourses in data split A
%             outputs.TsetB : (time x components) matrix of component timecourses in data split B

%--------------------------------------------------------------------------------------------------- 
%  RUN_RCAA: wrapper script that runs the reproducible Canonical Autocorrelation Analaysis (rCAA)
%  algorithm, used to identify a set of orthonormal timeseries that are (a) maximally 
%  autocorrelated in time and (b) highly spatially reproducible.
%  This has the extra feature that you can search for components that have central frequency 
%  in a specific frequency band (details below).
%--------------------------------------------------------------------------------------------------- 
%
% Syntax:
%          run_rCAA( input_file1, input_file2, mask_name, TR, band_select, out_prefix )
%
% Input:
%        input_file1,2 = two strings giving the path+name of runs of fMRI data 
%                          e.g.  input_file1 = 'my_directory/subject1_run1.nii',
%                                input_file2 = 'my_directory/subject1_run2.nii',
%                         This algorithm requires 2 runs ; they do not need to have the same number 
%                         of timepoints (although they should be somewhat close in size to ensure stability)
%        mask_name      = string specifying path+name of binary brain mask used to remove non-brain 
%                         tissue. PHYCAA+ is multivariate, and thus sensitive to non-brain confounds
%               TR      = acquisition time intervals (in sec.)
%        band_select    = 2D vector, specifying the frequency range (in Hz) where components' central frequency
%                         must be, to select in CAA model. Formatted as "band_select = [Low_threshold High_threshold]"
%                         If you don't want to constrain components by frequency, just set as empty (e.g. band_select=[]).
%        out_prefix     = prefix name for output physiological stats. If empty (outsuffix=[]),
%                         the default prefix is 'rCAA_new'
%
% Output: produces the following data...
%      
%    (1) matfile with name [out_prefix,'_rCAA_out.mat'], containing
%        'outputs' a structure with the following elements:
%
%             outputs.rep   : spatial reproducibility of CAA components
%             outputs.SPM   : (voxels x components) matrix of Z-scored, reproducible component spatial maps
%             outputs.TsetA : (time x components) matrix of component timecourses in data split A
%             outputs.TsetB : (time x components) matrix of component timecourses in data split B
%
%    (2) NIFTI volume containing Z-scored component SPMs, denoted [out_prefix,'_rCAA_spms.nii']

