% this code regresses voxel-wise difference in variance and covariance pre
% and post retroicor against the difference in cardiac and respiratory
% spectral power pre and post retroicor. Only significant voxels with
% positive correlation (i.e., z>0, where z is Fisher transformed r,
% thresholded at FDR=0.05) are considered.
% The code uses the frequency bands identified manually on the cardiac
% pulsation and respiration signals using power_spectra.m.
% this version, moreover, works with images in the MNI space, and only
% considers points with significant group variation in FC.


basepath='/home/mkayvanrad/data/healthyvolunteer/processed/retroicorpipe/';
ndiscard=10;
TR=0.380; % seconds (for current fast EPI data)
obase='/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/';

groupSPMfile='/home/mkayvanrad/data/healthyvolunteer/processed/retroicorpipe/z_thresh_prepostmatchedpairst.nii.gz';

% output files
fout=fopen(strcat(obase,'varcovar_vs_power_mni_significantFC.csv'),'w');

fprintf(fout,'Subject, var_b_card, var_b_resp, var_r2, var_p, cov_b_card, cov_b_resp, cov_r2, cov_p\n');

%% compute relative poweres
fin=fopen('/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/physio.csv');
% read the header
h=textscan(fin,'%s%s%s%s%s%s%s',1,'delimiter',',');
% read the rest
phys=textscan(fin,'%s%s%f%f%s%f%f','delimiter',',');

n=length(phys{1});

for i=1:n
    
    subject=cell2mat(phys{1}(i));
    
    preSPMfile=strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_z_thresh_mni152.nii.gz');
    postSPMfile=strcat(basepath,subject,'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_z_thresh_mni152.nii.gz');
    precovfile=strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_cov_mni152.nii.gz');
    postcovfile=strcat(basepath,subject,'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_cov_mni152.nii.gz');
    prevarfile=strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_var_mni152.nii.gz');
    postvarfile=strcat(basepath,subject,'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_var_mni152.nii.gz');
    prePrespfile=strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_Presp_mni152.nii.gz');
    postPrespfile=strcat(basepath,subject,'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_Presp_mni152.nii.gz');
    prePcardfile=strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_Pcard_mni152.nii.gz');
    postPcardfile=strcat(basepath,subject,'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_Pcard_mni152.nii.gz');
    
   
    preSPM_mri = MRIread(preSPMfile);
    preSPM=preSPM_mri.vol;    
    
    postSPM_mri = MRIread(postSPMfile);
    postSPM=postSPM_mri.vol;   
    
    precov_mri = MRIread(precovfile);
    precov=precov_mri.vol;    
    
    postcov_mri = MRIread(postcovfile);
    postcov=postcov_mri.vol;
    
    prevar_mri = MRIread(prevarfile);
    prevar=prevar_mri.vol;    
    
    postvar_mri = MRIread(postvarfile);
    postvar=postvar_mri.vol;

    prePresp_mri = MRIread(prePrespfile);
    prePresp=prePresp_mri.vol;    
    
    postPresp_mri = MRIread(postPrespfile);
    postPresp=postPresp_mri.vol;    

    prePcard_mri = MRIread(prePcardfile);
    prePcard=prePcard_mri.vol;    
    
    postPcard_mri = MRIread(postPcardfile);
    postPcard=postPcard_mri.vol;
    
    groupSPM_mri = MRIread(groupSPMfile);
    groupSPM=groupSPM_mri.vol;
    
%     %% compute frequency power spectra
%     % discarding frames at the beginning
%     preBOLD=preBOLD(:,:,:,ndiscard+1:end);
%     postBOLD=postBOLD(:,:,:,ndiscard+1:end);
%     % now compute voxel-wise fft
%     F_pre=fft(preBOLD,[],4);
%     F_post=fft(postBOLD,[],4);
%     % now compute power at resp and card frequency bands
%     fresp_min=phys{6}(i);
%     fresp_max=phys{7}(i);
%     fcard_min=phys{3}(i);
%     fcard_max=phys{4}(i);
% 
%     l=size(F_pre,4);
%     fs=1/TR;
% 
%     fresp_min_ind=ceil(fresp_min/(fs/2)*l/2);
%     fresp_max_ind=ceil(fresp_max/(fs/2)*l/2);
%     fcard_min_ind=ceil(fcard_min/(fs/2)*l/2);
%     fcard_max_ind=ceil(fcard_max/(fs/2)*l/2);

    Presp_pre=prePresp;
    Presp_post=postPresp;
    Pcard_pre=prePcard;
    Pcard_post=postPcard;    
    
    %% compute deltas
    deltaPresp=Presp_post-Presp_pre;
    deltaPcard=Pcard_post-Pcard_pre;
    deltaVar=postvar-prevar;
    deltaCov=postcov-precov;
    deltaZ=postSPM-preSPM;
    
    
%     % while here save the results in nifti files
%     mriout=prevar_mri;
%     %mriout.nframes=1;
%     mriout.vol=Presp_pre;
%     err = MRIwrite(mriout,strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_Presp.nii.gz'),'float');    
% 
%     mriout.vol=Pcard_pre;
%     err = MRIwrite(mriout,strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_Pcard.nii.gz'),'float');    
% 
%     mriout.vol=Presp_post;
%     err = MRIwrite(mriout,strcat(basepath,subject,'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_Presp.nii.gz'),'float');    
% 
%     mriout.vol=Pcard_post;
%     err = MRIwrite(mriout,strcat(basepath,subject,'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_Pcard.nii.gz'),'float');    
    
    % only consider voxels where there is significant chang
    deltaPresp=deltaPresp(~isnan(groupSPM));
    deltaPcard=deltaPcard(~isnan(groupSPM));
    deltaVar=deltaVar(~isnan(groupSPM));
    deltaCov=deltaCov(~isnan(groupSPM));
    deltaZ=deltaZ(~isnan(groupSPM));
    
    c=1.5;
    outlier= (deltaPresp > (quantile(deltaPresp,0.75) + c * iqr(deltaPresp)) | deltaPresp < (quantile(deltaPresp,0.25) - c * iqr(deltaPresp))) | ...
        (deltaPcard > (quantile(deltaPcard,0.75) + c * iqr(deltaPcard)) | deltaPcard < (quantile(deltaPcard,0.25) - c * iqr(deltaPcard))) | ...
        (deltaVar > (quantile(deltaVar,0.75) + c * iqr(deltaVar)) | deltaVar < (quantile(deltaVar,0.25) - c * iqr(deltaVar))) | ...
        (deltaCov > (quantile(deltaCov,0.75) + c * iqr(deltaCov)) | deltaCov < (quantile(deltaCov,0.25) - c * iqr(deltaCov)));
    
    samp=~outlier;
    deltaPresp=deltaPresp(samp);
    deltaPcard=deltaPcard(samp);
    deltaVar=deltaVar(samp);
    deltaCov=deltaCov(samp);
    
    %% regression
    
    lm_var=fitlm([deltaPcard,deltaPresp],deltaVar);
    lm_cov=fitlm([deltaPcard,deltaPresp],deltaCov);
    
    fprintf(fout,'%s,',subject);
    fprintf(fout,'%f,%f,%f,%f,',[lm_var.Coefficients.Estimate(2),lm_var.Coefficients.Estimate(3),lm_var.Rsquared.Ordinary,lm_var.coefTest]);
    fprintf(fout,'%f,%f,%f,%f\n',[lm_cov.Coefficients.Estimate(2),lm_cov.Coefficients.Estimate(3),lm_cov.Rsquared.Ordinary,lm_cov.coefTest]);
    
%     figure(i+40)
%     scatter3(deltaPcard,deltaPresp,deltaVar)
%     
%     
%     figure(i+60)
%     scatter3(deltaPcard,deltaPresp,deltaCov)
    
    
%     figure(i+20)
%     subplot(2,1,1)
%     lm_var.plot
%     %title('Var vs. Card & Resp Power')
%     axis tight
%     subplot(2,1,2)
%     lm_cov.plot
%     %title('Cov vs. Card & Resp Power')    
%     axis tight
    
    %% plot
    lm_var_card=fitlm(deltaPcard,deltaVar);
    figure(i)
    subplot(2,2,1)
    lm_var_card.plot
    legend('off')
    title('Var vs. Card Power')
    xlabel('')
    ylabel('dVar')
    axis tight
    
    lm_var_card=fitlm(deltaPresp,deltaVar);
    figure(i)
    subplot(2,2,2)
    lm_var_card.plot
    legend('off')
    title('Var vs. Resp Power')
    xlabel('')
    ylabel('')
    axis tight    

    lm_var_card=fitlm(deltaPcard,deltaCov);
    figure(i)
    subplot(2,2,3)
    lm_var_card.plot
    legend('off')
    title('Cov vs. Card Power')
    xlabel('dP')
    ylabel('dCov')
    axis tight
    
    lm_var_card=fitlm(deltaPresp,deltaCov);
    figure(i)
    subplot(2,2,4)
    lm_var_card.plot
    legend('off')
    title('Cov vs. Resp Power')
    xlabel('dP')
    ylabel('')
    axis tight    
    
end

fclose(fout);

