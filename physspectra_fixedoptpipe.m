% this code reads mean time series over CSF, WM, GM, and the network (e.g., motor
% network in the case of current fast EPI data set) and plots their power
% spectra for the fixed and optimal pipelines.
% It also calculates and compares relative
% power in the cardiac pulsation and respiration bands for the fiexed and
% optimal pipeline and saves the results into csv files. The code uses the
% frequency bands identified manually on the cardiac pulsation and
% respiration signals using power_spectra.m.


basepath='/home/mkayvanrad/data/healthyvolunteer/processed/retroicorpipe/';
ndiscard=10;
TR=0.380; % seconds (for current fast EPI data)


%% compute relative poweres
% read the following frequencies on the resp and puls frequency specra

ffixedlist=fopen('/home/mkayvanrad/data/healthyvolunteer/processed/retroicorpipe/fixed_pipe_netmeants.txt');
foptlist=fopen('/home/mkayvanrad/data/healthyvolunteer/processed/retroicorpipe/opt_pipe_r_netmeants.txt');

fin=fopen('/home/mkayvanrad/Dropbox/Projects/Physiological Noise Correction/Publications/ISMRM 2017/Results/physio.csv');
fcardout=fopen('/home/mkayvanrad/Dropbox/Projects/Pipeline/Publications/ISMRM 2018/Results/cardPowerSpectra.csv','w');
frespout=fopen('/home/mkayvanrad/Dropbox/Projects/Pipeline/Publications/ISMRM 2018/Results/respPowerSpectra.csv','w');
flowout=fopen('/home/mkayvanrad/Dropbox/Projects/Pipeline/Publications/ISMRM 2018/Results/lowPowerSpectra.csv','w');
% read the header
h=textscan(fin,'%s%s%s%s%s%s%s',1,'delimiter',',');

% read the rest
phys=textscan(fin,'%s%s%f%f%s%f%f','delimiter',',');

fprintf(fcardout,'Subject, NetcardRelativePowerPre, NetcardRelativePowerPost \n');
fprintf(frespout,'Subject, NetrespRelativePowerPre,NetrespRelativePowerPost \n');
fprintf(flowout,'Subject, NetlowRelativePowerPre,NetlowRelativePowerPost\n');

n=length(phys{1});

for i=1:n
    
    subject=cell2mat(phys{1}(i));
    
    fixedfile=fgetl(ffixedlist);
    optfile=fgetl(foptlist);
    
    %% read mean time series
    meants_preRetcorNet_fid=fopen(fixedfile);
    meants_preRetcorNet=fscanf(meants_preRetcorNet_fid,'%f');

    meants_postRetcorNet_fid=fopen(optfile);
    meants_postRetcorNet=fscanf(meants_postRetcorNet_fid,'%f');

    %% discarding frames at the beginnig
    meants_preRetcorNet=meants_preRetcorNet(ndiscard+1:end);
    meants_postRetcorNet=meants_postRetcorNet(ndiscard+1:end);

    %% plot power specra
    % compute FFTs
    Fmeants_preRetcorNet=fft(meants_preRetcorNet);
    Fmeants_postRetcorNet=fft(meants_postRetcorNet);

    %% plot
    l=length(Fmeants_preRetcorNet);
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
    
    NetrespRelativePowerPre=sum(abs(Fmeants_preRetcorNet(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_preRetcorNet).^2);
    NetrespRelativePowerPost=sum(abs(Fmeants_postRetcorNet(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_postRetcorNet).^2);
    NetcardRelativePowerPre=sum(abs(Fmeants_preRetcorNet(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_preRetcorNet).^2);
    NetcardRelativePowerPost=sum(abs(Fmeants_postRetcorNet(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_postRetcorNet).^2);
    
    NetlowRelativePowerPre=sum(abs(Fmeants_preRetcorNet(flow_min_ind:flow_max_ind)).^2)/sum(abs(Fmeants_preRetcorNet).^2);
    NetlowRelativePowerPost=sum(abs(Fmeants_postRetcorNet(flow_min_ind:flow_max_ind)).^2)/sum(abs(Fmeants_postRetcorNet).^2);
    
    card=[NetcardRelativePowerPre,NetcardRelativePowerPost];
    mat2str(card)
    fprintf(fcardout,'%s,',subject);
    fprintf(fcardout,'%f,%f\n',card);
    
    resp=[NetrespRelativePowerPre,NetrespRelativePowerPost];
    fprintf(frespout,'%f,%f\n',resp);
    
    low=[NetlowRelativePowerPre,NetlowRelativePowerPost];
    fprintf(flowout,'%s,',subject);
    fprintf(flowout,'%f,%f\n',low);

end

fclose(fcardout);
fclose(frespout);
