function output2 = run_PHYCAA_plus( input_cell, mask_name, prior_name, task_SPM_names, dataInfo, num_steps, out_prefix )
%
%==========================================================================
%  RUN_PHYCAA_PLUS: wrapper script that runs the 2-stage PHYCAA+ algorithm,
%  used to correct for physiological noise. Takes in names of 4D fMRI data
%  in NIFTI format, and outputs denoised NIFTI data.
%==========================================================================
%
% SYNTAX:
%
%   run_PHYCAA_plus( input_cell, mask_name, prior_name, task_SPM_names, dataInfo, num_steps, out_prefix )
%
% INPUT:
%
%   input_cell     = cell array of strings, each giving path/name of a run 
%                    of fMRI data
%                     e.g.  input_cell{1}= 'my_directory/subject1_run1.nii'
%                           input_cell{2}= 'my_directory/subject1_run2.nii'
%                             ....
%                    If you only have 1 run, it will do split-half noise
%                    estimation (e.g. slightly different than multi-run)
%                    Multiple runs do not require the same number of 
%                    timepoints (but they should be close to ensure stability)
%   mask_name      = string specifying path/name of binary brain mask used 
%                    to remove non-brain tissue - required to run PHYCAA+.
%   prior_name     = Parameter of STEP-1. OPTIONAL string specifying 
%                    path/name of binary brain mask with probable non-
%                    neuronal tissue locations (e.g. a CSF atlas). If 
%                    included, this step selects a threshold for masking 
%                    out voxels (voxel weight =0) that maximizes overlap 
%                    with the prior mask. Otherwise, the model masks out 
%                    the top 5% of voxels (average prior-based threshold 
%                    idenfified in Churchill & Strother 2013). If not 
%                    included, leave this entry empty (e.g. prior_name=[])
%   task_SPM_names = Parameter of STEP-2. An OPTIONAL single string or cell 
%                    array of strings; each giving the path/name of an 
%                    analysis SPM, used to estimate the residual subspace 
%                    in Step-2 of PHYCAA+, before physio. component estimation.
%                      e.g.   task_SPM_names    = 'my_directory/spm.nii'
%                         
%                       or    task_SPM_names{1} = 'my_directory/spmA.nii'
%                             task_SPM_names{2} = 'my_directory/spmB.nii'
%                              ...
%                    if you don't want to estimate the residual subspace, 
%                    leave this entry empty (e.g. task_SPM_names = []). 
%    dataInfo     =  a structure with the following fields. Only "TR" must 
%                    be specified, the rest are optional:
%
%                    dataInfo.TR         : Parameter of STEP-1. Rate of data acquisition (in sec.)
%                    dataInfo.FreqCut    : Parameter of STEP-1. High-frequency threshold in Hz, for which 
%                                          f > FreqCut is primarily  physiological noise. If not specified, 
%                                          DEFAULT value is FreqCut=0.10.
%                    dataInfo.comp_crit  : Parameter of STEP-2. Determines how conservative physiological 
%                                          component selection is. Value can range (0 <= comp_crit < 1), 
%                                          where a larger comp_crit indicates more conservative selection, 
%                                          i.e. variance must be more concentrated in non-neuronal tissue. 
%                                          DEFAULT value is comp_crit=0, which gives robust results.
%                    dataInfo.keepmean   : Parameter of STEP-2. PHYCAA+ subtracts voxel means of each run,
%                                          before component estimation.
%                                             0= voxel means are discarded 
%                                             1= voxel means re-added after noise regression
%                                          If not specified, DEFAULT value is keepmean=0.
%                    dataInfo.make_output: A general output parameter.
%                                             0= do NOT produced preprocessed data (just physiological maps, components etc.) 
%                                             1= produce preprocessed data as well (e.g. down-weight and/or noise regression) 
%                                          If not specified, DEFAULT value is make_output=1; preprocessed 
%                                          data are automatically created 
%
%   out_prefix   = prefix for physio output. If empty (out_prefix=[]), 
%                  DEFAULT prefix is 'PHYCAA_new'
%   num_steps    = integer indicates how many steps of PHYCAA+ to perform:
%                    1= do STEP1 only,  output (a) non-neuronal map, (b) downweighted data
%                    2= do STEP1+STEP2, output (a) non-neuronal map, (b) physio component map, (c) downweighted+regressed data
%
% OUTPUT:
%        if( num_steps==1 )
%                         (1) IF( dataInfo.out_format==1 ), downweighted fMRI datasets, denoted [input_cell{r}(1:end-4),'_PHYCAA_step1.nii']
%                         (2) non-neuronal weighting map, as a NIFTI volume [out_prefix,'_NN_map.nii']
%                         (3) matfile [out_prefix,'_PHYCAA_step1.mat'], containing outputs of PHYCAA+ step-1
%
%        if( num_steps==2 )
%                         (1) IF( dataInfo.out_format==1 ), downweighted+regressed fMRI datasets, denoted [input_cell{r}(1:end-4),'_PHYCAA_step1+2.nii']
%                         (2) non-neuronal weighting map, as a NIFTI volume [out_prefix,'_NN_map.nii']
%                         (3) Z-scored map of physiological component variance, as NIFTI volume  [out_prefix,'_Physio_Zmap.nii']
%                         (4) matfile [out_prefix,'_PHYCAA_step1+2.mat'], containing outputs of PHYCAA+ steps -1 and -2
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
% version history: 2014/03/27
% ------------------------------------------------------------------------%

%% (1) preparatory step

disp('Initializing PHYCAA+...');

% if single run as character array, convert to cell
if(ischar(input_cell))
    intmp{1} = input_cell;
    input_cell=intmp;
end

Nruns    = length( input_cell );          % number of runs (cell entries)
M        = load_untouch_nii( mask_name ); % load mask NIFTI
mask     = double(M.img>0);               % get 3d volume

% now load all run volumes into 2D voxels x time matrices
%
if( Nruns == 1 ) %% if only 1 run, split into halves
    
    % initialize cell matrix of data -- 2 splits
    datacell = cell(2,1);
    %
    V=load_untouch_nii( input_cell{1} ); 
    datatmp = nifti_to_mat(V,M); 
    % split it in half!
    Ntime = size(datatmp,2);
    datacell{1} = datatmp(:,              1:ceil(Ntime/2));
    datacell{2} = datatmp(:,ceil(Ntime/2)+1:end          );

else %% if >1 run, store unsplitted runs
    
    % initialize cell matrix of data -- Nruns
    datacell = cell(Nruns,1);
    %
    for( r=1:Nruns )
       %
       V=load_untouch_nii( input_cell{r} ); 
       datacell{r} = nifti_to_mat(V,M); 
       %
    end    
end

% check if vascular prior mask is specified
if( isempty(prior_name) )
    %
    disp('    (no spatial prior on PHYCAA+ step-1)');
    % if not, set the "noprior" value for PHYCAA+
    dataInfo.priorMask = [];
    dataInfo.thresh_method = 'noprior';
else
    %
    disp('    (spatial prior included for PHYCAA+ step-1)');
    % if included, load and convert to vect, set "prior" value for PHYCAA+
    P=load_untouch_nii( prior_name ); 
    dataInfo.priorMask = nifti_to_mat(P,M); 
	dataInfo.thresh_method = 'prior';
end

% Checking for signal spms -- to estimate residual subspace in step-2
if( isempty( task_SPM_names ) )
    %
    % if no spms are given, make empty matrix
    dataInfo.task_SPMs = [];    
    %
elseif( iscell(task_SPM_names) )
    %
    % if multiple spms, count #spms
    Nspms  = length( task_SPM_names );
    % initialize matrix
    spmmat = zeros( sum(mask(:)), Nspms );
    % fill in all spms
    for( r=1:Nspms )
       %
       S=load_untouch_nii( task_SPM_names{r} ); 
       spmmat(:,r) = nifti_to_mat(S,M); 
    end
    %
    dataInfo.task_SPMs = spmmat;
    %
elseif( ischar(task_SPM_names) )
    % 
    % if only one spm, load directly
    S=load_untouch_nii( task_SPM_names ); 
    dataInfo.task_SPMs = nifti_to_mat(S,M); 
    %
end
% if output is not specified, automatically create it
if( ~isfield(dataInfo, 'make_output') )
    %
    disp('    (default make_output=1)');
    %
    dataInfo.make_output = 1;
end

% designate prefix if unspecified
if( isempty(out_prefix) ) out_prefix = ['PHYCAA_new']; end

%% (2) physiological noise estimation steps

%%% ------------------- ONLY STEP-1 PERFORMED ------------------- %%%
if( num_steps == 1 )
    
    % if output turned on, set this parameter for step-1 code
    dataInfo.out_format = dataInfo.make_output;

    % output: down-weighted data
    output1 = PHYCAA_plus_step1( datacell, dataInfo );
    
    % generate downweighted fmri data, if specified
    if( dataInfo.make_output == 1 )

        if( Nruns == 1 ) %% if only 1 data-run available
                %
                weightedmat = [output1.dataMat_weighted{1} output1.dataMat_weighted{2}];
                TMPVOL      = zeros( [size(mask), size(weightedmat,2)] );
                %
                for(t=1:size(weightedmat,2) )
                    tmp=mask;tmp(tmp>0)=weightedmat(:,t);
                    TMPVOL(:,:,:,t) = tmp;
                end
                % --- convert to nifti
                %
                nii     = V; % copy nifti struct
                nii.img = TMPVOL; % replace volume
                nii.hdr.dime.datatype=16;
                nii.hdr.dime.dim([1 5])=[4 size(TMPVOL,4)];
                %
                save_untouch_nii(nii,[ input_cell{1}(1:end-4), '_PHYCAA_step1.nii' ]); 
            
        else             %% if multiple runs available
            
            for( r=1:Nruns )
                %
                weightedmat = output1.dataMat_weighted{r};
                TMPVOL      = zeros( [size(mask), size(weightedmat,2)] );
                %
                for(t=1:size(weightedmat,2) )
                    tmp=mask;tmp(tmp>0)=weightedmat(:,t);
                    TMPVOL(:,:,:,t) = tmp;
                end
                % --- convert to nifti
                %
                nii     = V; % copy nifti struct
                nii.img = TMPVOL; % replace volume
                nii.hdr.dime.datatype=16;
                nii.hdr.dime.dim([1 5])=[4 size(TMPVOL,4)];
                %
                save_untouch_nii(nii,[ input_cell{r}(1:end-4), '_PHYCAA_step1.nii' ]); 
            end
        end
    end
    %
    % save downweight map
    tmp=mask;tmp(tmp>0)=output1.NN_weight;
    TMPVOL = tmp;
    % --- convert to nifti
    %
    nii     = V; % copy nifti struct
    nii.img = TMPVOL; % replace volume
    nii.hdr.dime.datatype=16;
    nii.hdr.dime.dim([1 5])=[4 size(TMPVOL,4)];
    %
    save_untouch_nii(nii,[out_prefix,'_NN_map.nii']);           
    
    % save output as matfile as well
    save([out_prefix,'_PHYCAA_step1.mat'],'output1');
    
%%% ------------------- BOTH STEP-1 AND STEP-2 PERFORMED ------------------- %%%
elseif( num_steps == 2 )
    
    % no output for stage 1, regardless of choice
    dataInfo.out_format = 0;        
    %
    % output: down-weighted data
    output1 = PHYCAA_plus_step1( datacell, dataInfo );  
    % put the downweighting map into the 'datainfo' structure
    dataInfo.physio_map = output1.NN_weight;
    
    % now generate output for step-2 if output turned on
    dataInfo.out_format = dataInfo.make_output;

    % output: regressed+downweighted data
    output2 = PHYCAA_plus_step2( datacell, dataInfo );    

    % generate regressed + downweighted fmri data
    if( dataInfo.make_output == 1 )
        
        if( Nruns == 1 ) % if only 1 data-run available
                %
                denoisedmat = [output2.dataMat_denoised{1} output2.dataMat_denoised{2}];
                TMPVOL      = zeros( [size(mask), size(denoisedmat,2)] );
                %
                for(t=1:size(denoisedmat,2) )
                    tmp=mask;tmp(tmp>0)=denoisedmat(:,t);
                    TMPVOL(:,:,:,t) = tmp;
                end
                % --- convert to nifti
                %
                nii     = V; % copy nifti struct
                nii.img = TMPVOL; % replace volume
                nii.hdr.dime.datatype=16;
                nii.hdr.dime.dim([1 5])=[4 size(TMPVOL,4)];
                %
                save_untouch_nii(nii,[ input_cell{1}(1:end-4), '_PHYCAA_step1+2.nii' ]); 
                
        else          % otherwise
            for( r=1:Nruns )

                denoisedmat = output2.dataMat_denoised{r};
                TMPVOL      = zeros( [size(mask), size(denoisedmat,2)] );
                %
                for(t=1:size(denoisedmat,2) )
                    tmp=mask;tmp(tmp>0)=denoisedmat(:,t);
                    TMPVOL(:,:,:,t) = tmp;
                end
                % --- convert to nifti
                %
                nii     = V; % copy nifti struct
                nii.img = TMPVOL; % replace volume
                nii.hdr.dime.datatype=16;
                nii.hdr.dime.dim([1 5])=[4 size(TMPVOL,4)];
                %
                save_untouch_nii(nii,[ input_cell{r}(1:end-4), '_PHYCAA_step1+2.nii' ]); 
            end
        end
    end

    % save downweight map
    tmp=mask;tmp(tmp>0)=output1.NN_weight;
    TMPVOL = tmp;
    % --- convert to nifti
    %
    nii     = V; % copy nifti struct
    nii.img = TMPVOL; % replace volume
    nii.hdr.dime.datatype=16;
    nii.hdr.dime.dim([1 5])=[4 size(TMPVOL,4)];
    %
    save_untouch_nii(nii,[out_prefix,'_NN_map.nii']);           
    
    % save physio map
    tmp=mask;tmp(tmp>0)=output2.Physio_SPM;
    TMPVOL = tmp;
    % --- convert to nifti
    %
    nii     = V; % copy nifti struct
    nii.img = TMPVOL; % replace volume
    nii.hdr.dime.datatype=16;
    nii.hdr.dime.dim([1 5])=[4 size(TMPVOL,4)];
    %
    save_untouch_nii(nii,[out_prefix,'_Physio_Zmap.nii']);  
    
    % save output as matfile as well
    save([out_prefix,'_PHYCAA_step1+2.mat'],'output1','output2');
end
   
%%
function dataMat = nifti_to_mat( niiVol, niiMask )
%
% take niiVol and niiMask (nifti) format, and convert
% to matlab vector/matrix structure:
%
% dataMat = nifti_to_mat( niiVol, niiMask )
%
vol = double(niiVol.img);
msk = double(niiMask.img);

dataMat = zeros( sum(msk(:)>0), size(vol,4) );

for(t=1:size(vol,4))
    tmp=vol(:,:,:,t);
    dataMat(:,t) = tmp(msk>0);
end

