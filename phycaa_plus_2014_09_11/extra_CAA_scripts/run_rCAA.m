function run_rCAA( input_file1, input_file2, mask_name, TR, band_select, out_prefix )
%
%==========================================================================
%  RUN_RCAA: wrapper script that runs the reproducible Canonical 
%  Autocorrelation Analaysis (rCAA) algorithm, used to identify a set of 
%  orthonormal timeseries that are (a) maximally autocorrelated in time and 
%  (b) highly spatially reproducible. This has the extra feature that you 
%  can search for components that have central frequency 
%  in a specific frequency band (details below).
%==========================================================================
%
% SYNTAX:
%
%   run_rCAA( input_file1, input_file2, mask_name, TR, band_select, out_prefix )
%
% INPUT:
%
%   input_file1,2 = two strings giving the path+name of runs of fMRI data 
%                     e.g.  input_file1 = 'my_directory/subject1_run1.nii',
%                           input_file2 = 'my_directory/subject1_run2.nii',
%                   This algorithm requires 2 runs ; they do not need to 
%                   have the same number of timepoints (although they 
%                   should be somewhat close in size to ensure stability)
%   mask_name     = string specifying path+name of binary brain mask used 
%                   to remove non-brain tissue. PHYCAA+ is multivariate, 
%                   and thus sensitive to non-brain confounds
%   TR            = acquisition time intervals (in sec.)
%   band_select   = 2D vector, specifying the frequency range (in Hz) where 
%                   components' central frequency must be, to select in CAA 
%                   model. Format as "band_select = [Low_threshold High_threshold]"
%                   If you don't want to constrain components by frequency, 
%                   just set as empty (e.g. band_select=[]).
%   out_prefix    = prefix name for output physiological stats. If empty 
%                   (outsuffix=[]), the default prefix is 'rCAA_new'
%
% OUTPUT: produces the following data...
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
%
% ------------------------------------------------------------------------%
%   Copyright 2013 Baycrest Centre for Geriatric Care
%
%   This file is part of the PHYCAA+ program. PHYCAA+ is free software: you 
%   can redistribute it and/or modify it under the terms of the GNU Lesser 
%   General Public License as published by the Free Software Foundation, 
%   either version 3 of the License, or (at your option) any later version.
% 
%   PHYCAA+ is distributed in the hope that it will be useful, but WITHOUT 
%   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
%   FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License 
%   for more details.
% 
%   You should have received a copy of the GNU General Lesser Public 
%   License along with PHYCAA+. If not, see <http://www.gnu.org/licenses/>.
% 
%   This code was developed by Nathan Churchill Ph.D., University of Toronto,
%   during his doctoral thesis work. Email: nchurchill@research.baycrest.org
%
%   Any use of this code should cite the following publication:
%      Churchill & Strother (2013). "PHYCAA+: An Optimized, Adaptive Procedure for 
%      Measuring and Controlling Physiological Noise in BOLD fMRI". NeuroImage 82: 306-325
%
% ------------------------------------------------------------------------%
% version history: 2013/07/21
% ------------------------------------------------------------------------%

% load mask volume
M=load_untouch_nii( mask_name );
mask     = double(M.img);
% load run1
V=load_untouch_nii( input_file1 ); 
datamat1 = nifti_to_mat(V,M); 
% load run2
V=load_untouch_nii( input_file2 ); 
datamat2 = nifti_to_mat(V,M); 

% designate output prefix if unspecified
if( isempty(out_prefix) ) out_prefix = ['rCAA_new']; end

% run  the rCAA algorithm
output = rCAA( datamat1, datamat2, TR, 1, band_select );
% save general output
save([out_prefix,'_rCAA_out.mat'],'output');
% number of components
Ncomp  = length( output.rep );
TMPVOL = zeros( [size(mask), Ncomp] );
%
for(t=1:Ncomp )
    tmp=mask;tmp(tmp>0)=output.SPM(:,t);
    TMPVOL(:,:,:,t) = tmp;
end
% --- convert to nifti
nii=make_nii( TMPVOL, V.hdr.dime.pixdim(2:4) );
nii.hdr.hist = V.hdr.hist;
nii.hdr.dime.dim(5) = Ncomp;
save_nii(nii,[ out_prefix,'_rCAA_spms.nii' ]); 
    