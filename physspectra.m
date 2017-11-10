% this code reads mean time series over CSF, WM, GM, and the network (motor
% network in the case of current fast EPI data set) and plots their power
% spectra pre and post retroicor. It also calculates and compares relative
% power in the cardiac pulsation and respiration bands pre and post
% retroicor and saves the results into csv files. The code uses the
% frequency bands identified manually on the cardiac pulsation and
% respiration signals using power_spectra.m.


basepath='/home/mkayvanrad/data/healthyvolunteer/processed/retroicorpipe/';
ndiscard=10;
TR=0.380; % seconds (for current fast EPI data)


%% compute relative poweres
% read the following frequencies on the resp and puls frequency specra

fin=fopen('/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/physio.csv');
fcardout=fopen('/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/cardPowerSpectra.csv','w');
frespout=fopen('/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/respPowerSpectra.csv','w');
flowout=fopen('/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/lowPowerSpectra.csv','w');
% read the header
h=textscan(fin,'%s%s%s%s%s%s%s',1,'delimiter',',');

% read the rest
phys=textscan(fin,'%s%s%f%f%s%f%f','delimiter',',');

fprintf(fcardout,'Subject, NetcardRelativePowerPre, NetcardRelativePowerPost, GMcardRelativePowerPre, GMcardRelativePowerPost, CSFcardRelativePowerPre, CSFcardRelativePowerPost, WMcardRelativePowerPre, WMcardRelativePowerPost \n');
fprintf(frespout,'Subject, NetrespRelativePowerPre,NetrespRelativePowerPost,GMrespRelativePowerPre,GMrespRelativePowerPost,CSFrespRelativePowerPre,CSFrespRelativePowerPost,WMrespRelativePowerPre,WMrespRelativePowerPost \n');
fprintf(flowout,'Subject, NetlowRelativePowerPre,NetlowRelativePowerPost\n');

n=length(phys{1});

for i=1:n
    
    subject=cell2mat(phys{1}(i));
    
    preRetcorCSFfile=strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_meants_csf.txt');
    preRetcorWMfile=strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_meants_wm.txt');
    preRetcorGMfile=strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_meants_gm.txt');
    preRetcorNetFile=strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_meants_net.txt');

    postRetcorCSFfile=strcat(basepath,subject,'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_meants_csf.txt');
    postRetcorWMfile=strcat(basepath,subject,'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_meants_wm.txt');
    postRetcorGMfile=strcat(basepath,subject,'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_meants_gm.txt');
    postRetcorNetFile=strcat(basepath,subject,'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_meants_net.txt');

    %% read mean time series
    meants_preRetcorCSF_fid=fopen(preRetcorCSFfile);
    meants_preRetcorCSF=fscanf(meants_preRetcorCSF_fid,'%f');

    meants_preRetcorWM_fid=fopen(preRetcorWMfile);
    meants_preRetcorWM=fscanf(meants_preRetcorWM_fid,'%f');

    meants_preRetcorGM_fid=fopen(preRetcorGMfile);
    meants_preRetcorGM=fscanf(meants_preRetcorGM_fid,'%f');

    meants_preRetcorNet_fid=fopen(preRetcorNetFile);
    meants_preRetcorNet=fscanf(meants_preRetcorNet_fid,'%f');


    meants_postRetcorCSF_fid=fopen(postRetcorCSFfile);
    meants_postRetcorCSF=fscanf(meants_postRetcorCSF_fid,'%f');

    meants_postRetcorWM_fid=fopen(postRetcorWMfile);
    meants_postRetcorWM=fscanf(meants_postRetcorWM_fid,'%f');

    meants_postRetcorGM_fid=fopen(postRetcorGMfile);
    meants_postRetcorGM=fscanf(meants_postRetcorGM_fid,'%f');

    meants_postRetcorNet_fid=fopen(postRetcorNetFile);
    meants_postRetcorNet=fscanf(meants_postRetcorNet_fid,'%f');

    %% discarding frames at the beginnig
    meants_preRetcorCSF=meants_preRetcorCSF(ndiscard+1:end);
    meants_preRetcorWM=meants_preRetcorWM(ndiscard+1:end);
    meants_preRetcorGM=meants_preRetcorGM(ndiscard+1:end);
    meants_preRetcorNet=meants_preRetcorNet(ndiscard+1:end);

    meants_postRetcorCSF=meants_postRetcorCSF(ndiscard+1:end);
    meants_postRetcorWM=meants_postRetcorWM(ndiscard+1:end);
    meants_postRetcorGM=meants_postRetcorGM(ndiscard+1:end);
    meants_postRetcorNet=meants_postRetcorNet(ndiscard+1:end);

    %% plot power specra
    % compute FFTs
    Fmeants_preRetcorCSF=fft(meants_preRetcorCSF);
    Fmeants_preRetcorWM=fft(meants_preRetcorWM);
    Fmeants_preRetcorGM=fft(meants_preRetcorGM);
    Fmeants_preRetcorNet=fft(meants_preRetcorNet);

    Fmeants_postRetcorCSF=fft(meants_postRetcorCSF);
    Fmeants_postRetcorWM=fft(meants_postRetcorWM);
    Fmeants_postRetcorGM=fft(meants_postRetcorGM);
    Fmeants_postRetcorNet=fft(meants_postRetcorNet);

    %% plot
    l=length(Fmeants_preRetcorCSF);
    fs=1/TR;
    f=fs*(0:l/2)/l;

%     %% plot CSF power spectra 
%     subplot(2,1,1)
%     plot(f,2*abs(Fmeants_preRetcorCSF(1:l/2+1))/l)
%     title('Mean BOLD time series over CSF pre Retroicor');
%     %xlabel('Frequency (Hz)')
%     ylabel('P(f)')
% 
%     subplot(2,1,2)
%     plot(f,2*abs(Fmeants_postRetcorCSF(1:l/2+1))/l)
%     title('Mean BOLD time series over CSF post Retroicor');
%     xlabel('Frequency (Hz)')
%     ylabel('P(f)')
% 
%     %% plot GM power spectra
%     figure(2)
% 
%     subplot(2,1,1)
%     plot(f,2*abs(Fmeants_preRetcorGM(1:l/2+1))/l)
%     title('Mean BOLD time series over GM pre Retroicor');
%     %xlabel('Frequency (Hz)')
%     ylabel('P(f)')
% 
%     subplot(2,1,2)
%     plot(f,2*abs(Fmeants_postRetcorGM(1:l/2+1))/l)
%     title('Mean BOLD time series over GM post Retroicor');
%     xlabel('Frequency (Hz)')
%     ylabel('P(f)')
% 
%     %% plot WM power spectra
%     figure(3)
% 
%     subplot(2,1,1)
%     plot(f,2*abs(Fmeants_preRetcorWM(1:l/2+1))/l)
%     title('Mean BOLD time series over WM pre Retroicor');
%     %xlabel('Frequency (Hz)')
%     ylabel('P(f)')
% 
%     subplot(2,1,2)
%     plot(f,2*abs(Fmeants_postRetcorWM(1:l/2+1))/l)
%     title('Mean BOLD time series over WM post Retroicor');
%     xlabel('Frequency (Hz)')
%     ylabel('P(f)')

    %% plot Network power spectra
    figure(i)

    subplot(3,1,1)
    plot(f,2*abs(Fmeants_preRetcorNet(1:l/2+1))/l)
    title('Pre Retroicor');
    %xlabel('Frequency (Hz)')
    ylabel('PSD (I^2/Hz)')

    subplot(3,1,2)
    plot(f,2*abs(Fmeants_postRetcorNet(1:l/2+1))/l)
    title('Post Retroicor');
    %xlabel('Frequency (Hz)')
    ylabel('PSD (I^2/Hz)')
    
    
    subplot(3,1,3)
    plot(f,2*abs(Fmeants_postRetcorNet(1:l/2+1))/l-2*abs(Fmeants_preRetcorNet(1:l/2+1))/l)
    title('Difference pre and post RETROICOR')
    xlabel('f(Hz)')
    ylabel('PSD (I^2/Hz)')

    fresp_min=phys{6}(i);
    fresp_max=phys{7}(i);
    fcard_min=phys{3}(i);
    fcard_max=phys{4}(i);
    
    % looking at low frequency
    flow_min=0.01;
    flow_max=0.1;

    l=length(Fmeants_preRetcorCSF);
    fs=1/TR;

    fresp_min_ind=ceil(fresp_min/(fs/2)*l/2);
    fresp_max_ind=ceil(fresp_max/(fs/2)*l/2);
    fcard_min_ind=ceil(fcard_min/(fs/2)*l/2);
    fcard_max_ind=ceil(fcard_max/(fs/2)*l/2);
    flow_min_ind=ceil(flow_min/(fs/2)*l/2);
    flow_max_ind=ceil(flow_max/(fs/2)*l/2);
    
    CSFrespRelativePowerPre=sum(abs(Fmeants_preRetcorCSF(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_preRetcorCSF).^2);
    CSFrespRelativePowerPost=sum(abs(Fmeants_postRetcorCSF(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_postRetcorCSF).^2);
    CSFcardRelativePowerPre=sum(abs(Fmeants_preRetcorCSF(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_preRetcorCSF).^2);
    CSFcardRelativePowerPost=sum(abs(Fmeants_postRetcorCSF(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_postRetcorCSF).^2);

    GMrespRelativePowerPre=sum(abs(Fmeants_preRetcorGM(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_preRetcorGM).^2);
    GMrespRelativePowerPost=sum(abs(Fmeants_postRetcorGM(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_postRetcorGM).^2);
    GMcardRelativePowerPre=sum(abs(Fmeants_preRetcorGM(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_preRetcorGM).^2);
    GMcardRelativePowerPost=sum(abs(Fmeants_postRetcorGM(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_postRetcorGM).^2);

    WMrespRelativePowerPre=sum(abs(Fmeants_preRetcorWM(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_preRetcorWM).^2);
    WMrespRelativePowerPost=sum(abs(Fmeants_postRetcorWM(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_postRetcorWM).^2);
    WMcardRelativePowerPre=sum(abs(Fmeants_preRetcorWM(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_preRetcorWM).^2);
    WMcardRelativePowerPost=sum(abs(Fmeants_postRetcorWM(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_postRetcorWM).^2);

    NetrespRelativePowerPre=sum(abs(Fmeants_preRetcorNet(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_preRetcorNet).^2);
    NetrespRelativePowerPost=sum(abs(Fmeants_postRetcorNet(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_postRetcorNet).^2);
    NetcardRelativePowerPre=sum(abs(Fmeants_preRetcorNet(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_preRetcorNet).^2);
    NetcardRelativePowerPost=sum(abs(Fmeants_postRetcorNet(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_postRetcorNet).^2);
    
    NetlowRelativePowerPre=sum(abs(Fmeants_preRetcorNet(flow_min_ind:flow_max_ind)).^2)/sum(abs(Fmeants_preRetcorNet).^2);
    NetlowRelativePowerPost=sum(abs(Fmeants_postRetcorNet(flow_min_ind:flow_max_ind)).^2)/sum(abs(Fmeants_postRetcorNet).^2);
    
    card=[NetcardRelativePowerPre,NetcardRelativePowerPost,GMcardRelativePowerPre,GMcardRelativePowerPost,CSFcardRelativePowerPre,CSFcardRelativePowerPost,WMcardRelativePowerPre,WMcardRelativePowerPost];
    mat2str(card)
    fprintf(fcardout,'%s,',subject);
    fprintf(fcardout,'%f,%f,%f,%f,%f,%f,%f,%f\n',card);
    
    resp=[NetrespRelativePowerPre,NetrespRelativePowerPost,GMrespRelativePowerPre,GMrespRelativePowerPost,CSFrespRelativePowerPre,CSFrespRelativePowerPost,WMrespRelativePowerPre,WMrespRelativePowerPost];
    fprintf(frespout,'%s,',subject);
    fprintf(frespout,'%f,%f,%f,%f,%f,%f,%f,%f\n',resp);
    
    low=[NetlowRelativePowerPre,NetlowRelativePowerPost];
    fprintf(flowout,'%s,',subject);
    fprintf(flowout,'%f,%f\n',low);

end

fclose(fcardout);
fclose(frespout);