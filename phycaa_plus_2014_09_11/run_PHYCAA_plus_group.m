function run_PHYCAA_plus_group( input_cell, mask_name, prior_name, task_SPM_names, dataInfo, num_steps, out_prefix )
%
%==========================================================================
%  RUN_PHYCAA_PLUS_GROUP: wrapper script that runs the 2-stage PHYCAA+ 
%  algorithm to correct for physiological noise, for multiple subjects 
%  simultaneously. Estimates a group average non-neuronal map, for cases
%  where a single, consistent vascular mask is required for all subjects
%==========================================================================
%
% SYNTAX:
%
%   run_PHYCAA_plus_group( input_cell, mask_name, prior_name, task_SPM_names, dataInfo, num_steps, out_prefix )
%
% INPUT:
%
%   input_cell    =  2-level cell array of strings. Each cell at first level 
%                    corresponds to a subject, and every subject cell contains 
%                    an array, indicating path+name of a run of fMRI data.
%                     e.g.   input_cell{1}{1}=  'my_directory/subject1_run1.nii'
%                            input_cell{1}{2} = 'my_directory/subject1_run2.nii'
%                                ...
%                            input_cell{2}{1} = 'my_directory/subject2_run1.nii'
%                            input_cell{2}{2} = 'my_directory/subject2_run2.nii'
%                                ...
%                            input_cell{3}{1} = 'my_directory/subject3_run1.nii'
%                            input_cell{3}{2} = 'my_directory/subject3_run2.nii'
%                                ...
%                    requires AT LEAST 2 subjects to run. Does NOT require
%                    the same number of timepoints across subjects/runs
%                    (though they should be close to ensure stability)
%   mask_name      = string specifying path/name of binary brain mask used 
%                    to remove non-brain tissue - required to run PHYCAA+.
%                    ** NB: one brain mask for all subjects/runs;
%                           everything should be in same coordinate space!  
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
%                  DEFAULT prefix is 'PHYCAA_group_new'
%   num_steps    = integer indicating how many steps of PHYCAA+ to perform:
%                    1= do STEP1 only,  output (a) non-neuronal map, (b) downweighted data
%                    2= do STEP1+STEP2, output (a) non-neuronal map, (b) physio component map, (c) downweighted+regressed data
%
% OUTPUT:
%        if( num_steps==1 )
%                         (1) IF( dataInfo.out_format==1 ), downweighted fMRI datasets, denoted [input_cell{r}(1:end-4),'_PHYCAA_step1_group.nii']
%                         (2) non-neuronal weighting map, as a NIFTI volume [out_prefix,'_NN_map_avg.nii']
%                         (3) matfile [out_prefix,'_PHYCAA_step1_group.mat'], containing outputs of PHYCAA+ step-1
%
%        if( num_steps==2 )
%                         (1) IF( dataInfo.out_format==1 ), downweighted+regressed fMRI datasets, denoted [input_cell{r}(1:end-4),'_PHYCAA_step1+2_group.nii']
%                         (2) non-neuronal weighting map, as a NIFTI volume [out_prefix,'_NN_map_avg.nii']
%                         (3) Z-scored map of physiological component variance, as NIFTI volume  [out_prefix,'_Physio_Zmap_avg.nii']
%                         (4) matfile [out_prefix,'_PHYCAA_step1+2_group.mat'], containing outputs of PHYCAA+ steps -1 and -2
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

disp('Initializing group PHYCAA+...');

% number of subjects
Nsubject    = length( input_cell );
% count number of runs for each subject
for(is=1:Nsubject)
    %
    Nruns(is,1) = length( input_cell{is} );
end
% load single group mask
M        = load_untouch_nii( mask_name ); % load mask NIFTI
mask     = double(M.img>0);               % get 3d volume

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
if( isempty(out_prefix) ) out_prefix = ['PHYCAA_group_new']; end

%% (2) physiological noise estimation steps

%%% ------------------- ONLY STEP-1 PERFORMED ------------------- %%%
if( num_steps == 1 ) 
    
    % even if output turned on, we don't get down-weighted output from step-1 code
    dataInfo.out_format = 0;

    % initialize cell array of step-1 outputs
    output1_group = cell(Nsubject,1);
    % initialize 2D matrix of non-neuronal weight maps
    nn_weight_set = zeros( sum(mask(:)), Nsubject );
    
    % Iterate Step-1, across subjects
    for(is=1:Nsubject)   
        
        disp(['PHYCAA+ Step-1. Running subject_',num2str(is),'/',num2str(Nsubject)]);

        if( Nruns(is) == 1 ) %% if only 1 runs is available, split in half
            
            % initialize cell array of data for subject "is"
            datacell = cell(2,1); 

            V=load_untouch_nii( input_cell{is}{1} ); 
            datatmp = nifti_to_mat(V,M); 
            % split it in half!
            Ntime = size(datatmp,2);
            datacell{1} = datatmp(:,              1:ceil(Ntime/2));
            datacell{2} = datatmp(:,ceil(Ntime/2)+1:end          );

        else  %% if multiple runs, store them unsplitted
            
            % initialize cell array of data for subject "is"
            datacell = cell(Nruns(is),1); 

            % now load all run volumes into 2D voxels x time matrices
            for( ir=1:Nruns(is) )
               %
               V=load_untouch_nii( input_cell{is}{ir} ); 
               datacell{ir} = nifti_to_mat(V,M); 
               %
            end
        end
        %
        % output: down-weighted data
        output1_group{is}   = PHYCAA_plus_step1( datacell, dataInfo );
        % put downweighted image into 2D matrix
        nn_weight_set(:,is) = output1_group{is}.NN_weight;
    end
    
    % compute robust average of non-neuronal maps
    NN_weight_avg = NN_group_average( nn_weight_set );

    % generate downweighted fmri data, if specified
    if( dataInfo.make_output == 1 )

        % Iterate across subjects
        for(is=1:Nsubject)   
            
            % load all run volumes into 2D voxels x time matrices
            for( ir=1:Nruns(is) )
               %
               V=load_untouch_nii( input_cell{is}{ir} ); 
               %
               datamat = nifti_to_mat(V,M); 
               TMPVOL  = zeros( [size(mask), size(datamat,2)] );
               %
                for(t=1:size(datamat,2) )
                    tmp=mask;tmp(tmp>0)=datamat(:,t) .* NN_weight_avg;
                    TMPVOL(:,:,:,t) = tmp;
                end
                % --- convert to nifti
                %
                nii     = V; % copy nifti struct
                nii.img = TMPVOL; % replace volume
                nii.hdr.dime.datatype=16;
                nii.hdr.dime.dim([1 5])=[4 size(TMPVOL,4)];
                %
                save_untouch_nii(nii,[ input_cell{is}{ir}(1:end-4), '_PHYCAA_step1_group.nii' ]); 
            end
        end
    end
        
    % save group-average downweight map
    tmp=mask;tmp(tmp>0)=NN_weight_avg;
    TMPVOL = tmp;
    % --- convert to nifti
    %
    nii     = V; % copy nifti struct
    nii.img = TMPVOL; % replace volume
    nii.hdr.dime.datatype=16;
    nii.hdr.dime.dim([1 5])=[4 size(TMPVOL,4)];
    %
    save_untouch_nii(nii,[out_prefix,'_NN_map_avg.nii']);           

    % save output as matfile as well
    save([out_prefix,'_PHYCAA_step1_group.mat'],'output1_group','NN_weight_avg');

%%% ------------------- BOTH STEP-1 AND STEP-2 PERFORMED ------------------- %%%
elseif( num_steps == 2 )
    
    % no output for stage 1, regardless of choice
    dataInfo.out_format = 0;        
    
    % initialize cell array of step-1 outputs
    output1_group = cell(Nsubject,1);
    % initialize 2D matrix of non-neuronal weight maps
    nn_weight_set = zeros( sum(mask(:)), Nsubject );
    % initialize 2D matrix of physio z-score maps
    zphys_map_set = zeros( sum(mask(:)), Nsubject );
    
    % Iterate Step-1, across subjects
    for(is=1:Nsubject)   
        
        disp(['PHYCAA+ Step-1. Running subject_',num2str(is),'/',num2str(Nsubject)]);

        if( Nruns(is) == 1 ) %% if only 1 run per subject
            
            % initialize cell array of data for subject "is"
            datacell = cell(2,1); 

            V=load_untouch_nii( input_cell{is}{1} ); 
            datatmp = nifti_to_mat(V,M); 
            % split it in half!
            Ntime = size(datatmp,2);
            datacell{1} = datatmp(:,              1:ceil(Ntime/2));
            datacell{2} = datatmp(:,ceil(Ntime/2)+1:end          );
            
        else %% if multiple runs available
        
            % initialize cell array of data for subject "is"
            datacell = cell(Nruns(is),1); 

            % now load all run volumes into 2D voxels x time matrices
            for( ir=1:Nruns(is) )
               %
               V=load_untouch_nii( input_cell{is}{ir} ); 
               datacell{ir} = nifti_to_mat(V,M); 
               %
            end
        end
        %
        % output: down-weighted data
        output1_group{is}   = PHYCAA_plus_step1( datacell, dataInfo );
        % put downweighted image into 2D matrix
        nn_weight_set(:,is) = output1_group{is}.NN_weight;
    end
    
    % compute robust average of non-neuronal maps
    NN_weight_avg = NN_group_average( nn_weight_set );
    % put the downweighting map into the 'datainfo' structure for step-2
    dataInfo.physio_map = NN_weight_avg;

%%
    % now generate output for step-2 if output turned on
    dataInfo.out_format = dataInfo.make_output;

    % Iterate Step-1, across subjects
    for(is=1:Nsubject)   
        
        disp(['PHYCAA+ Step-2. Running subject_',num2str(is),'/',num2str(Nsubject)]);

        if( Nruns(is) == 1 ) %% if only 1 run available per subject
            
            % initialize cell array of data for subject "is"
            datacell = cell(2,1); 

            V=load_untouch_nii( input_cell{is}{1} ); 
            datatmp = nifti_to_mat(V,M); 
            % split it in half!
            Ntime = size(datatmp,2);
            datacell{1} = datatmp(:,              1:ceil(Ntime/2));
            datacell{2} = datatmp(:,ceil(Ntime/2)+1:end          );

        else %% if multiple runs available

            % initialize cell array of subjectt data
            datacell = cell(Nruns(is),1); 

            % now load all run volumes into 2D voxels x time matrices
            for( ir=1:Nruns(is) )
               %
               V=load_untouch_nii( input_cell{is}{ir} ); 
               datacell{ir} = nifti_to_mat(V,M); 
               %
            end
        end
        %
        % output: regressed+downweighted data
        output2_group{is}   = PHYCAA_plus_step2( datacell, dataInfo );
        
        % generate regressed + downweighted fmri data
        if( dataInfo.make_output == 1 )
            
            if( Nruns(is) == 1 ) %% if only 1 run available per subject
                
                    denoisedmat = [output2_group{is}.dataMat_denoised{1} output2_group{is}.dataMat_denoised{2}];
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
                    save_untouch_nii(nii,[input_cell{is}{1}(1:end-4), '_PHYCAA_step1+2_group.nii' ]); 

            else %% if multiple runs available
                
                for( ir=1:Nruns(is) )

                    denoisedmat = output2_group{is}.dataMat_denoised{ir};
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
                    save_untouch_nii(nii,[input_cell{is}{ir}(1:end-4), '_PHYCAA_step1+2_group.nii' ]); 
                end
            end
        end
        % now clear out denoised dataMats (otherwise data cell will be very large!)
        output2_group{is}.dataMat_denoised = [];
        % ---
        zphys_map_set(:,is) = output2_group{is}.Physio_SPM;
    end
    
    % save group average downweight map
    tmp=mask;tmp(tmp>0)=NN_weight_avg;
    TMPVOL = tmp;
    % --- convert to nifti
    %
    nii     = V; % copy nifti struct
    nii.img = TMPVOL; % replace volume
    nii.hdr.dime.datatype=16;
    nii.hdr.dime.dim([1 5])=[4 size(TMPVOL,4)];
    %
    save_untouch_nii(nii,[out_prefix,'_NN_map_avg.nii']);           

    % save group average downweight map
    tmp=mask;tmp(tmp>0)=mean(zphys_map_set,2);
    TMPVOL = tmp;
    % --- convert to nifti
    %
    nii     = V; % copy nifti struct
    nii.img = TMPVOL; % replace volume
    nii.hdr.dime.datatype=16;
    nii.hdr.dime.dim([1 5])=[4 size(TMPVOL,4)];
    %
    save_untouch_nii(nii,[out_prefix,'_Physio_Zmap_avg.nii']);               
    
    % save output as matfile as well
    save([out_prefix,'_PHYCAA_step1+2_group.mat'],'output1_group','output2_group','NN_weight_avg');
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

