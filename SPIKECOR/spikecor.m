function output = spikecor( volname, maskname, mpename, outprefix, OUT_PARAM, interpname  )
%
% THIS SCRIPT HAS BEEN MODIFIED BY ARAS KAYVANRAD
% FOR USE WITH THE FMRI PIPELINE TOOL
%
%
% =========================================================================
%  SPIKECOR: This script provides a quick, computationally efficient test
%  for outlier volumes in fMRI, typically produced by head motion "spikes".
%  It takes in fMRI data, a brain mask and (optional) Motion Parameter
%  Estimates (MPEs); these are used to remove motion outliers and replace
%  them with interpolated values.
% =========================================================================
%
% SYNTAX:
%
%         spikecor( volname, maskname, mpename, outprefix, OUT_CORRECT, interpname  )
%
% INPUT:
%         volname   = string, giving path/name of input fMRI data
%                     must be 4D fMRI data in NIFTI or ANALYZE format
%         maskname  = string, giving path/name of binary brain mask (to exclude non-brain tissue)
%                     must be 3D fMRI volume in NIFTI to ANALYZE format
%         mpename   = string, giving path/name of MPE file
%                     must be a 6-column textfile, giving 6 rigid-body parameter timerseries
%
%        outprefix  = optional string giving output path for (1) QC output, and (2) diagnostic figures. 
%                     If outprefix=[], uses 'volname' as the default
%
%        OUT_PARAM  = string determines which criteria are used to identify outliers
%                     and interpolate over them. OUT_PARAM options:
%
%                     'none'         : do not discard outliers  (for diagnostic purposes only)
%                     'motion'       : replace outlier volumes, based on MPE values
%                     'volume'       : replace outlier volumes, based on fMRI PCA distribution
%                     'volume+motion': replace outlier volumes, based on MPEs & fMRI PCA distribution
%                     'slice'        : replace outlier slices,  based on fMRI single-slice PCA distribution
%                     'slice+motion' : replace outlier slices,  based on MPEs & fMRI single-slice PCA distribution
% 
%                     * we recommend conservative choice 'volume+motion' as a starting point.
%
%        interpname = string specifying the full path+name of the de-spiked fMRI data output.
%                     (e.g. interpname = 'mypath/subject_data_1_interp.nii')
%
% OUTPUT:
% 
%  (1) Interpolated fMRI data, labeled "interpname", provided OUT_PARAM != 'none'
%
%  (2) an "output" structure, saved to [outprefix,'_QC_output.mat'] with fields:
%
%      [Censor vectors] Binary vectors of length (time x 1), where (1=non-outliers) and (0=outliers). 
%        These are used to remove and interpolate outliers if OUT_PARAM != 'none':
%
%        output.censor_mot   : significant outlier in MPEs
%        output.censor_vol   : significant outlier in fMRI data
%        output.censor_volmot: significant outlier in BOTH fMRI data and MPEs**
%
%      [Censor matrices] A new feature! Binary matrices of size (time x brain slices)
%        where (1=non-outliers) and (0=outliers). This gives outliers for individual
%        axial brain slices, and can be used as input to remove outlier slices:
%
%        output.censor_slc   : significant outlier in fMRI slice data
%        output.censor_slcmot: significant outlier in BOTH fMRI slice data and MPEs**
%
%     ** for (censor_volmot) and (censor_slcmot), we discard fMRI outliers
%        if they occur at same time OR +1 TR after a motion spike. This
%        allows for delayed fMRI-related signal changes (e.g. spin-history effects)
%
%      [Other possibly useful outputs] 
%
%       output.eigimages_fmri: matrix (voxel x K) PCA eigenimages for fMRI data (K=PCs explaining 95% of variance)
%       output.eigvect_fmri  : matrix (time x K) PCA eigen-timeseries for fMRI data 
%       output.eigfract_fmri : vector (K x 1) of fraction of variance explained by each PC of fMRI data
%
%       output.eigweights_mot: matrix (6    x 6) PCA weights on motion parameters for MPEs
%       output.eigvect_mot   : matrix (time x 6) PCA eigen-timeseries for MPEs
%       output.eigfract_mot  : vector (6 x 1) of fraction of variance explained by each PC of MPEs
%
%  (3) Quality Control output figures. The figures include:
%
%       "<outprefix>_diagnostic_plot0.png" : summary results for temporal variance in data
%       "<outprefix>_diagnostic_plot1.png" : summary results from PCA decomposition of data
%       "<outprefix>_diagnostic_plot2.png" : results for estimated motion spikes
%
%      Please see README for more details on what figures represent
%
% ------------------------------------------------------------------------------------------- 
% Outlier Testing Protocol:
%
%  - Takes 4D fMRI data, converted into (voxels x time) matrix, and performs PCA
%    decomposition. Similarly, MPE matrix (time x 6 parameters) is decomposed 
%    with PCA. This gives an efficient, orthonormal representation of the data.
%    Aso plots PCA information about data (eg eigenspectra) to characterize better
%
%  - For outlier detection: 
%    We want to find spikes (brief, large signal changes) in multidimensional data.
%    We estimate outliers in the MPE and fMRI data:
%
%    1. For each datapoint X(t) (1 <= t <= N_time):
%        (a) find median PC-space coordinate Xmed(t), in a 15 TR timewindow centered at t
%        (b) compute displacement by Euclidean distance D(t) = L2( X(t) - Xmed(t) )
%    2. For displacement timeseries D, compute Gamma distribution on D^2
%        using Maximum Likelihood fit to infer degrees of freedom.
%    3. Identify outliers, significant at p<0.05
%
%  - We measure displacement relative to a 15-TR time window:
%    This has the advantage over (1) a simple derivative, e.g. we can discriminate 
%    displacement AWAY from the main datapoint cluster vs. discplement back TOWARDS
%    this cluster. The windowing also (2) minimizes the impact of slow changes
%    in amplitude over time, which might inflate our displacement estimates.
%  - If we do slice-specific outlier testing, this whole process is repeated independently 
%    for each axial brain slice
%
%  - For outlier removal:
%    We identify outlier volumes/slices, based on the chosen statistical
%    criterion (specified in OUT_PARAM). Outlier volumes/slices are discarded 
%    and replaced using cubic-spline interpolation from neighbouring volumes.
%    Unlike simply discarding motion spikes, this avoids any issues of
%    sharp discontinuities in the timeseries, and is less sensitive to data
%    and power loss from motion spikes
%
% ------------------------------------------------------------------------%
%   Copyright 2013 Baycrest Centre for Geriatric Care
%
%   This file is part of the SPIKECOR program. SPIKECOR is free software: you 
%   can redistribute it and/or modify it under the terms of the GNU Lesser 
%   General Public License as published by the Free Software Foundation, 
%   either version 3 of the License, or (at your option) any later version.
% 
%   SPIKECOR is distributed in the hope that it will be useful, but WITHOUT 
%   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
%   FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License 
%   for more details.
% 
%   You should have received a copy of the GNU General Lesser Public 
%   License along with SPIKECOR. If not, see <http://www.gnu.org/licenses/>.
% 
%   This code was developed by Nathan Churchill Ph.D., University of Toronto,
%   Email: nchurchill@research.baycrest.org
%
%   Any use of this code should cite the following publication:
%       Campbell K, Grigg O, Saverino C, Churchill N, Grady C. (in press). 
%       Age Differences in the Intrinsic Functional Connectivity of Default Network Subsystems.
%       Frontiers in Human Neuroscience.
%
% ------------------------------------------------------------------------%
% version history: 2013/11/29
% ------------------------------------------------------------------------%

if( exist('OCTAVE_VERSION','builtin') ) %% test if platform is Octave
    % load stats packages
    pkg load statistics;
    pkg load optim; 
end

%% (0) PREPARATION

% add the path for code used to convert NIFTI files into matrices
addpath NIFTI_tools;

% formatting the output data name: make sure an output name exists
if( isempty(outprefix) ) 
    % if not, make it a trimmed version of output name
    idx     = strfind(volname,'/');
    % drop the suffix / input directory bits
    if( isempty( idx ) )
            outprefix = volname( 1           :(end-4) ); 
    else    outprefix = volname( (idx(end)+1):(end-4) ); 
    end
end

% load fMRI NIFTI-format data into MatLab
VV     = load_untouch_nii(volname); % load 4D fMRI dataset
vol    = double(VV.img);
dims = size(vol);

% load mask or, if not available, assume the entire image
if ~isempty(maskname)
    MM     = load_untouch_nii(maskname);% load the binary brain mask
    mask   = double(MM.img);
else
    mask = ones(dims(1:3));
end

% load the motion parameters (matrix of [time x 6] elements) or, if not
% given, assume zero
if ~isempty(mpename)
    MPE    = load(mpename);
else
    MPE = zeros(size(vol,4),6);
end

% mean-center (subtract the mean from each timecourse)
MPE    = MPE - repmat( mean(MPE), [size(MPE,1) 1] );

% convert 4D fMRI data into (voxels x time) matrix
rawepi = convert_nii_to_mat( vol, mask ); 
% mean-center (subtract mean from each voxel
epimat = rawepi - repmat( mean(rawepi,2), [1 size(rawepi,2)] );
% get fMRI data matrix dimensions
[Nvox Ntime] = size(rawepi);

% catch #1: identify cases where #TRs does not match between fMRI and MPE
if( size( epimat,2 ) ~= size(MPE,1) )
    %
    error('number of timepoints in fMRI data and MPE data do not match!');
end
% catch #2: identify cases where mask and 4D EPI volumes are not the same size
dimsV = size(vol(:,:,:,1));
dimsM = size(mask(:,:,:,1));
%
if( (dimsV(1)~=dimsM(1)) || (dimsV(2)~=dimsM(2)) || (dimsV(3)~=dimsM(3)) )
    %
    error('dimensions of mask and 4D fMRI data do not match!');
end

%% (1) MOTION OUTLIER TESTING

% singular value decomposition (get the principal components of MPEs)
[u s v] = svd(MPE','econ');
   s2   = s.^2;                % squared eigenvalues
   p    = diag(s2)./trace(s2); % fraction of variance explained by each PC
% project data onto PC space (each timepoint = PC-space column vector)
Qmot    = (v * s)'; 

% initialize distance measures
Dist_mot2 = zeros(Ntime,1);
% run through timepoints (1...Ntime)
for(t=1:Ntime)
    % estimate 15-TR time window
    wind=[(t-7):(t-1), (t+1):(t+7)];
    if(wind( 1 )< 1   ) wind(wind<1)     = []; end
    if(wind(end)>Ntime) wind(wind>Ntime) = []; end
                        wind(wind==i)    = [];
	% get distance estimate at each timepoint, relative to median coordinate
    Dist_mot2(t,1)=sum(( Qmot(:,t) - median( Qmot(:,wind),2 ) ).^2);
end
%
% Gamma fit of MPEs (using gamma distribution, ML estimator)
Dist_mot2_norm = Dist_mot2 ./ max(Dist_mot2);
par_ab         = gamfit( Dist_mot2_norm );
% get Gamma probability of each point + outlier threshold
probGam_mot    = 1-gamcdf( Dist_mot2_norm, par_ab(1), par_ab(2) );
outThr_mot     = gaminv( 0.95, par_ab(1), par_ab(2) );

%% (2) FULL BRAIN-VOLUME OUTLIER TESTING

% singular value decomposition, on full fMRI data matrix
[V S2 temp] = svd( epimat'*epimat ); 
   S   = sqrt(S2);
   U   = epimat*V*inv(S);
   P   = diag(S2) ./ trace( S2 );
% project data onto PC space (each timepoint = PC-space column vector)
Qvol   = (V * S)';

% initialize distance measures
Dist_vol2 = zeros(Ntime , 1);
Qtraj     = zeros( size(Qvol,1), Ntime);
% run through data timepoints (1...Ntime)
for(t=1:Ntime)
    % estimate 15-TR time window
    wind=[(t-7):(t-1), (t+1):(t+7)];
    if(wind( 1 )< 1   ) wind(wind<1)     = []; end
    if(wind(end)>Ntime) wind(wind>Ntime) = []; end
                        wind(wind==i)    = [];
	% get distance estimate at each timepoint, relative to median coordinate
    Dist_vol2(t,1)=sum(( Qvol(:,t) - median( Qvol(:,wind),2 ) ).^2);
    %
    Qtraj(:,t) = mean( Qvol(:,wind),2 );
end
% Gamma fit full volume fMRI data (using gamma distribution, ML estimator)
Dist_vol2_norm = Dist_vol2 ./ max(Dist_vol2);
par_ab         = gamfit( Dist_vol2_norm );
% get Gamma probability of each point + outlier threshold
probGam_vol   = 1-gamcdf( Dist_vol2_norm, par_ab(1), par_ab(2) );
outThr_vol     = gaminv( 0.95, par_ab(1), par_ab(2) );

%% (3) SLICE-BASED OUTLIER TESTING

% get 3D volume dimensions
[Nx Ny Nz] = size( mask );
% get index-vector, where each voxel is labelled with its slice# (z=1...Nz)
ixvol = ones( [Nx Ny Nz] );
for(z=1:Nz) ixvol(:,:,z) = ixvol(:,:,z) .* z; end
ixvect = ixvol(mask>0);

% initialize distance/probability values
outThr_slc     =       ones(   1,  Nz  ); %threshold=1
probGam_slc    =       ones( Ntime, Nz ); %prob of outlier=1
Dist_slc2_norm = 0.001*ones( Ntime, Nz ); %zero displacement

% iterate through each brain slice
for( z=1:Nz )
    
    % check for signal in slice
    fullsum = sum(sum(abs(epimat(ixvect==z,:))));
    
    % requires that there be signal in this slice
    if( (fullsum~=0) && isfinite( fullsum ) )
        
        % singular value decomposition on individual fMRI data slice
        [V_tmp S2_tmp temp] = svd( epimat(ixvect==z,:)'*epimat(ixvect==z,:) ); 
         S_tmp  = sqrt(S2_tmp./sum(ixvect==z));
        % project data onto PC space (each timepoint = PC-space column vector)
         Qslc   = (V_tmp * S_tmp)';
         
        % initialize distance measures
        Dist_tmp2 = zeros(Ntime , 1);
        % run through timepoints (1...Ntime)
        for(t=1:Ntime)
            % estimate 15-TR time window
            wind=(t-7):(t+7);
            if(wind( 1 )< 1   ) wind(wind<1)     = []; end
            if(wind(end)>Ntime) wind(wind>Ntime) = []; end
                                wind(wind==i)    = [];
            % get distance estimate at each timepoint, relative to median coordinate
            Dist_tmp2(t,1)=sum(( Qslc(:,t) - median( Qslc(:,wind),2 ) ).^2);
        end

        % Gamma fit, individual fMRI data slice (using gamma distribution, ML estimator)
        Dist_tmp2_norm = Dist_tmp2 ./ max(Dist_tmp2);
        par_ab         = gamfit( Dist_tmp2_norm );
        % get Gamma probability of each point + outlier threshold
        probGam_tmp    = 1-gamcdf( Dist_tmp2_norm, par_ab(1), par_ab(2) );
        outThr_slc(1,z)= gaminv( 0.95, par_ab(1), par_ab(2) );
        %
        Dist_slc2_norm(:,z) = Dist_tmp2_norm;
        probGam_slc(:,z)    = probGam_tmp;
    end
end

 % Rescale slice-based distance values, so that =1 indicates significant outlier
 Dist_slc2_rescal = Dist_slc2_norm ./ repmat( outThr_slc, [size(Dist_slc2_norm,1) 1] );
 % Get significant outliers, based on each metric
 outlier_mot   = double( probGam_mot <= 0.05 );
 outlier_vol   = double( probGam_vol <= 0.05 );
 outlier_slc   = double( probGam_slc <= 0.05 );

 % find outliers in fMRI data, that have motion outlier concurrently, or 1TR before
 % -accounts for potential delay effects
 outlier_delay = double( (outlier_mot + [0; outlier_mot(1:end-1)]) > 0 );
 outlier_volmot= outlier_vol .* outlier_delay;
 outlier_slcmot= outlier_slc .* repmat( outlier_delay, [1 Nz] );
 
% outliers based on volume/motion only
  maxout    = round( 0.10*Ntime );
% -------- test for excessive outliers ------- %
if( sum(outlier_mot ) > maxout ) disp( 'WARNING: more than 10% of motion points are outliers!'); end
if( sum(outlier_vol ) > maxout ) disp( 'WARNING: more than 10% of fMRI data points are outliers!'); end

%% (4) PLOTTING RESULTS

% Only plot output if operating in matlab
if( exist('OCTAVE_VERSION','builtin') )
    %
    disp(['figures not plotted in Octave']);
else
    % ----------- (Fig.0) Display Temporal Variance information ----------- %

    h0=figure('visible','off');
    set(gcf, 'Units', 'normalized');
    set(gcf, 'Position', [0.10 0.15 0.60 0.65]);

    stdvol = std(double(VV.img),0,4);
    slcx = permute( stdvol(round(Nx/2),:,:), [3 2 1] );
    slcy = permute( stdvol(:,round(Ny/2),:), [3 1 2] );
    slcz = stdvol(:,:,round(Nz/2));

    slcall= [slcx(:); slcy(:); slcz(:)];

    subplot(2,3,1); imagesc( flipud(slcx), prctile( slcall(slcall~=0), [2.5 97.5] ));
    set(gca, 'xtick',[],'ytick',[]);
    subplot(2,3,2); imagesc( flipud(slcy), prctile( slcall(slcall~=0), [2.5 97.5] )); title('Temporal Standard Deviation plots');
    set(gca, 'xtick',[],'ytick',[]);
    subplot(2,3,3); imagesc( slcz, prctile( slcall(slcall~=0), [2.5 97.5] ));
    set(gca, 'xtick',[],'ytick',[]);

    subplot(2,1,2);
    % pre-get vectors
    gsvect  = zscore( mean(epimat)' ); 
    fpcvect = zscore( V(:,1) ); fpcvect = fpcvect .* sign( corr(fpcvect, gsvect) );
    mpcvect = zscore( v(:,1) ); mpcvect = mpcvect .* sign( corr(mpcvect,fpcvect) );
    %Current leftout: plots the relationship between fMRI and MPE first PCs
    plot( 1:Ntime,fpcvect,'.-k', 1:Ntime, gsvect, '.-r', 1:Ntime,mpcvect,'.-b' , 'markersize',8, 'linewidth',1.5 ); 
    cc1 = abs(corr( mpcvect, fpcvect ));
    cc2 = abs(corr(  gsvect, fpcvect ));
    legend('MPE-PC','fMRI-PC','fMRI-GS');
    text(3,  3.7, strcat('R^2(FMRI-PC,MPE-PC ) = ',num2str( round(cc1*100) ),'%'));
    text(3, -3.7, strcat('R^2(FMRI-PC,FMRI-GS) = ',num2str( round(cc2*100) ),'%'));
    ylim([-4.2 4.2]);
    title('Principal Component #1, and fMRI global-mean timecourses');
    xlabel('time (TR)');
    ylabel('z-score units');

    saveas(h0,strcat(outprefix,'_diagnostic_plot0.png'));
    close(h0);

    % ----------- (Fig.1) Display PCA-based information ----------- %

    h0=figure('visible','off');
    set(gcf, 'Units', 'normalized');
    set(gcf, 'Position', [0.10 0.05 0.60 0.85]);

    subplot(2,2,1); % plot1: plot datapoints in pca space (dim1+2)
    hold on;
    pbound = 1.1*max(abs(Qvol(1,:)));
    plot( pbound*[-1 1], [0 0], '-k', [0 0], pbound*[-1 1], '-k', 'color',[0.75 0.75 0.75] );
    plot( Qvol(1,:), Qvol(2,:), 'ok', 'markerfacecolor','b', 'markersize',4);
    plot( Qtraj(1,:), Qtraj(2,:), '--r', 'linewidth',2);
    text( Qtraj(1,1), Qtraj(2,1), ['T=1'],'color','r' );
    text( Qtraj(1,end), Qtraj(2,end), ['T=',num2str(Ntime)],'color','r' );
    title('Scans in PCA-space'); xlabel('PC-1'); ylabel('PC-2');
    %
    xlim([-pbound pbound]);
    ylim([-pbound pbound]);

    subplot(2,2,2); % plot3: eigenspectrum
    plot( 1:6,p,'o-b', 1:10, P(1:10), 'o-k', 'markersize',6, 'linewidth',1.5 ); 
    ylim([0 1]); xlim([0.5 10.5]);
    legend('MPEs','fMRI');
    title('Fractional eigenspectrum'); xlabel('PC#'); ylabel('fraction of total variance');
    set(gca,'Ytick',[0.1:0.1:1.0],'gridlinestyle',':','ygrid','on')

    % ---------------------------

    vertvect = sum(sum(mask,1),2);
    aidx     = find( vertvect(:) > 0 );
    seg      = floor(length(aidx)./5);
    %
    tmp=mask;tmp(tmp>0)=U(:,1); pbound = prctile( abs(U(:,1)), 95 );
    slc = [tmp(:,:,aidx(1)+1*seg) tmp(:,:,aidx(1)+2*seg); tmp(:,:,aidx(1)+3*seg) tmp(:,:,aidx(1)+4*seg)];
    subplot(2,2,3); imagesc( slc, [-pbound pbound] );
    title('PC Eigenimage #1');
    set(gca, 'xtick',[],'ytick',[]);
    %
    tmp=mask;tmp(tmp>0)=U(:,2); pbound = prctile( abs(U(:,2)), 95 );
    slc = [tmp(:,:,aidx(1)+1*seg) tmp(:,:,aidx(1)+2*seg); tmp(:,:,aidx(1)+3*seg) tmp(:,:,aidx(1)+4*seg)];
    subplot(2,2,4); imagesc( slc, [-pbound pbound] );
    title('PC Eigenimage #2');
    set(gca, 'xtick',[],'ytick',[]);

    saveas(h0,strcat(outprefix,'_diagnostic_plot1.png'));
    close(h0);

    % ----------- (Fig.2) Display Motion-linked information ----------- %

    h0=figure('visible','off');
    set(gcf, 'Units', 'normalized');
    set(gcf, 'Position', [0.10 0.05 0.60 0.85]);
    % 
    subplot(3,2,1);
    plot( 1:Ntime, sqrt(Dist_mot2_norm), '.-b', [1 Ntime], [1 1]*sqrt(outThr_mot), ':r' );
    title('MPE displacement (fraction of max.)');
    xlabel('time (TR)'); ylabel('amplitude (a.u.)');
    xlim([0 Ntime+1]); ylim([-0.05 1.05]);
    %
    subplot(3,2,3);
    plot( 1:Ntime, sqrt(Dist_vol2_norm), '.-b', [1 Ntime], [1 1]*sqrt(outThr_vol), ':r' );
    title('FMRI volume displacement (fraction of max.)');
    xlabel('time (TR)'); ylabel('amplitude (a.u.)');
    xlim([0 Ntime+1]); ylim([-0.05 1.05]);
    %
    subplot(3,2,5);
    imagesc( [outlier_mot';outlier_vol';2.*outlier_volmot'], [0 1.5] );
    title('significant outliers');
    text(-10, 1,'MPE');
    text(-10, 2,'fMRI');
    text(-10, 3,'Both');
    xlabel('time (TR)');
    set(gca,'YTickLabel',['';'';'']);
    %
    subplot( 2,2,2 );
    imagesc( Dist_slc2_rescal', [0 1] );
    title('FMRI slice displacements (fraction of max.)');
    xlabel('time (TR)');
    ylabel('slice');
    %
    subplot( 2,2,4 );
    imagesc( outlier_slc' + outlier_slcmot', [0 1.5] );
    title('significant outliers');
    xlabel('time (TR)');
    ylabel('slice');

    saveas(h0,strcat(outprefix,'_diagnostic_plot2.png'));
    close(h0);
end

% Some output text:

disp(sprintf('\n\nDone. Diagnostic results...\n')),
numsignif = sum( cumsum(P) < 0.95 )+1;
disp(strcat('>  1-',num2str(numsignif),' PCs required to explain 95% of fMRI variance'));

if( sum( outlier_mot ) ==0 ) disp( '(1) No motion outliers identified.' );
else                         disp( '(1) Possible motion outliers at timepoints:' ); disp( find( outlier_mot(:)' > 0 ) );
end
%
if( sum( outlier_volmot ) ==0 ) disp( '(2) No fMRI volume +motion outliers identified.' );
else                         disp( '(2) Possible fMRI volume +motion outliers at timepoints:' );   disp( find( outlier_volmot(:)' > 0 ) );
end
if( sum( sum(outlier_slcmot,2) ) ==0 ) disp( '(3) No fMRI slice +motion outliers identified.' );
else                         disp( '(3) Possible fMRI slice +motion outliers at timepoints:' );   disp( find( sum(outlier_slcmot,2)' > 0 ) );
end

%% (5) Define "output" structure and save

% censor files, where 1=non-outlier, and 0=significant outlier
output.censor_mot    = 1-outlier_mot;
output.censor_vol    = 1-outlier_vol;
output.censor_slc    = 1-outlier_slc;
output.censor_volmot = 1-outlier_volmot;
output.censor_slcmot = 1-outlier_slcmot;
% fmri - pca data
output.eigimages_fmri = U(:, 1:(sum(cumsum(P)<0.95)+1));
output.eigvect_fmri   = V(:, 1:(sum(cumsum(P)<0.95)+1));
output.eigfract_fmri  = P( 1:(sum(cumsum(P)<0.95)+1) );
% motion - pca data
output.eigweights_mot = u;
output.eigvect_mot    = v;
output.eigfract_mot   = p;

% save results to matfile
if( exist('OCTAVE_VERSION','builtin') )
     % matlab-compatible
     save( strcat(outprefix,'_QC_output.mat'), 'output', '-mat7-binary' );    
else save( strcat(outprefix,'_QC_output.mat'), 'output' );
end

%% (6) RUN INTERPOLATION ("CENSORING") IF REQUESTED

% outputs "censored" data if OUT_PARAM != 'none'
%
% first, check output parameters:
switch lower( OUT_PARAM )
    
    case 'none'   
                % 0. terminate if not interpolation requested
                disp('No interpolation...');   return;
    case 'motion'   
                % 1. use motion parameters only
                X_cens = output.censor_mot;    byslice=0;
    case 'volume'   
                % 2. use fmri volume data only
                X_cens = output.censor_vol;    byslice=0;
    case 'slice' 
                % 3. use fmri axial slice data only
                X_cens = output.censor_slc;    byslice=1;
    case 'volume+motion' 
                % 4. use fmri volume + motion parameters
                X_cens = output.censor_volmot; byslice=0;
    case 'slice+motion'
                % 5. use fmri axial slices + motion parameters
                X_cens = output.censor_slcmot; byslice=1;
    otherwise
                % terminate if OUT_PARAM setting is not on list
                error('censoring format not recognized.');
end

% If interpolation is on full volumes and/or motion parameters
if( byslice==0 )

    % check for no outliers
    if( isempty(find(X_cens==0,1,'first')) )
        disp('No outlier points to remove.');
        %
        VX = VV;
        save_untouch_nii(VX,interpname);
    else
        disp('Removing outliers.');
        vimg      = double(VV.img);
        [Nx Ny Nz Nt] = size(vimg);
        % convert to matfile data
        volmat = reshape(vimg,[],Nt);

        % ------------------------------------------------

        TimeList     = 1:Nt;
        % catch outliers at run endpoints -- we don't want to extrapolate values, as this is unstable
        idx  = find(X_cens>0); %uncensored points
        % if point 1=outlier, make it same as first non-outlier
        if( X_cens(1) == 0 ) 
            X_cens(1) =  1;
            volmat(:,1) = volmat(:,idx(1));
        end
        % if endpoint=outlier, make it same as last non-outlier
        if( X_cens(Nt)==0 )
            X_cens(Nt) = 1;
            volmat(:,Nt) = volmat(:,idx(end));
        end
        %
        subTimeList = TimeList(X_cens>0);
        subvolmat   = volmat(:,X_cens>0)';
        %
        interpvolmat = interp1( subTimeList, subvolmat, TimeList,'cubic' );
        interpvolmat = interpvolmat';

        vimg_interp = reshape(interpvolmat,Nx,Ny,Nz,Nt);
        %
        VX = VV;
        VX.img = vimg_interp;
        save_untouch_nii(VX,interpname);        
    end

% If interpolation IS slice-by-slice...
elseif( byslice==1 )

    % check for no outliers
    if( isempty(find(X_cens(:)==0,1,'first')) )
        %
        disp('No outlier points to remove.');
        %
        VX = VV;
        save_untouch_nii(VX,interpname);
    else
        disp('Removing outliers.');
        vimg      = double(VV.img);
        [Nx Ny Nz Nt] = size(vimg);
        %
        % temprah for volume creation
        ixvol = ones( [Nx Ny Nz] );
        for(z=1:Nz) ixvol(:,:,z) = ixvol(:,:,z) .* z; end
        ixvect = reshape(ixvol,[],1);
        % convert to matfile data
        volmat = reshape(vimg,[],Nt); 
        % make this same as original, only overwrite needed slc
        interpvolmat = volmat;
        %
        for( z=1:Nz )

            X_slcCens = X_cens(:,z);

            if( ~isempty(find(X_slcCens==0,1,'first')) )

                slcmat    = volmat( ixvect==z, : );

                % ------------------------------------------------

                TimeList     = 1:Nt;
                % catch outliers at run endpoints -- we don't want to extrapolate values, as this is unstable
                idx  = find(X_cens>0); %uncensored points
                % if point 1=outlier, make it same as first non-outlier
                if( X_slcCens(1) == 0 ) 
                    X_slcCens(1) =  1;
                    slcmat(:,1) = slcmat(:,idx(1));
                end
                % if endpoint=outlier, make it same as last non-outlier
                if( X_slcCens(Nt)==0 )
                    X_slcCens(Nt) = 1;
                    slcmat(:,Nt) = slcmat(:,idx(end));
                end
                %
                subTimeList = TimeList(X_slcCens>0);
                subslcmat   = slcmat(:,X_slcCens>0)';
                %
                interpslcmat = interp1( subTimeList, subslcmat, TimeList,'cubic' );
                interpvolmat(ixvect==z,:) = interpslcmat';
            end
        end
        %
        vimg_interp = reshape(interpvolmat,Nx,Ny,Nz,Nt);
        %
        VX = VV;
        VX.img = vimg_interp;
        save_untouch_nii(VX,interpname);
    end
end    

%%
function dataMat = convert_nii_to_mat( vol, msk )
%
% take niiVol and niiMask (nifti) format, and convert
% to matlab vector/matrix structure:
%
% dataMat = convert_nii_to_mat( niiVol, niiMask )
%

%vol = double(niiVol.img);
%msk = double(niiMask.img);

ldim = size(vol);

if( length( ldim ) < 4 )
   
    dataMat = vol(msk>0);
else   
    fullMsk = repmat( msk, [1,1,1,ldim(4)] );
    dataMat = reshape( vol(fullMsk>0), [], ldim(4) );
end
