% this code reads mean time series over CSF, WM, GM, and the network (motor
% network in the case of current fast EPI data set) and plots their power
% spectra pre and post retroicor. It also calculates and compares relative
% power in the cardiac pulsation and respiration bands pre and post
% retroicor

basepath='/home/mkayvanrad/data/healthyvolunteer/processed/retroicorpipe_temp/';
subject='7130/20140312';
ndiscard=10;
TR=0.380; % seconds (for current fast EPI data)
fs_phys=50;

preRetcorCSFfile=strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_mcflirt_slicetimer_ssmooth_3dFourier_brainExtractFSL_meants_csf.txt');
preRetcorWMfile=strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_mcflirt_slicetimer_ssmooth_3dFourier_brainExtractFSL_meants_wm.txt');
preRetcorGMfile=strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_mcflirt_slicetimer_ssmooth_3dFourier_brainExtractFSL_meants_gm.txt');
preRetcorNetFile=strcat(basepath,subject,'/fepi/fepi_pipeline_noRet_mcflirt_slicetimer_ssmooth_3dFourier_brainExtractFSL_meants_net.txt');

postRetcorCSFfile=strcat(basepath,subject,'/fepi/fepi_pipeline_mcflirt_slicetimer_ssmooth_3dFourier_retroicor_brainExtractFSL_meants_csf.txt');
postRetcorWMfile=strcat(basepath,subject,'/fepi/fepi_pipeline_mcflirt_slicetimer_ssmooth_3dFourier_retroicor_brainExtractFSL_meants_wm.txt');
postRetcorGMfile=strcat(basepath,subject,'/fepi/fepi_pipeline_mcflirt_slicetimer_ssmooth_3dFourier_retroicor_brainExtractFSL_meants_gm.txt');
postRetcorNetFile=strcat(basepath,subject,'/fepi/fepi_pipeline_mcflirt_slicetimer_ssmooth_3dFourier_retroicor_brainExtractFSL_meants_net.txt');

pulsfile='/home/mkayvanrad/data/healthyvolunteer/physio/7130/20140312/pulstrace/8fmri102a7130.puls.1D';
respfile='/home/mkayvanrad/data/healthyvolunteer/physio/7130/20140312/Biopac/7130_20140312_08.resp.1D';

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

puls_fid=fopen(pulsfile);
puls=fscanf(puls_fid,'%f');

resp_fid=fopen(respfile);
resp=fscanf(resp_fid,'%f');

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

Fpuls=fft(puls);
Fresp=fft(resp);

% plot
figure(1)
l=length(Fmeants_preRetcorCSF);
fs=1/TR;
f=fs*(0:l/2)/l;

subplot(2,1,1)
plot(f,2*abs(Fmeants_preRetcorCSF(1:l/2+1))/l)
title('Mean BOLD time series over CSF pre Retroicor');
%xlabel('Frequency (Hz)')
ylabel('P(f)')

subplot(2,1,2)
plot(f,2*abs(Fmeants_postRetcorCSF(1:l/2+1))/l)
title('Mean BOLD time series over CSF post Retroicor');
xlabel('Frequency (Hz)')
ylabel('P(f)')

figure(11)
l=length(Fresp);
f=fs_phys*(0:l/2)/l;
maxind=ceil((1/TR)/fs_phys*l/2); % to align with BOlD spectrum
plot(f(1:maxind),2*abs(Fresp(1:maxind))/l)
title('Respiration Freq. Spectrum');
xlabel('Frequency (Hz)')
ylabel('P(f)')

figure(12)
l=length(Fpuls);
f=fs_phys*(0:l/2)/l;
maxind=ceil((1/TR)/fs_phys*l/2); % to align with BOlD spectrum
plot(f(1:maxind),2*abs(Fpuls(1:maxind))/l)
title('Cardiac pulsation Freq. Spectrum');
xlabel('Frequency (Hz)')
ylabel('P(f)')

%% compute relative poweres
% read the following frequencies on the resp and puls frequency specra
fresp_min=0.15;
fresp_max=0.25;

fcard_min=1.15;
fcard_max=1.25;

l=length(Fmeants_preRetcorCSF);
fs=1/TR;

fresp_min_ind=ceil(fresp_min/(fs/2)*l/2);
fresp_max_ind=ceil(fresp_max/(fs/2)*l/2);
respRelativePowerPre=sum(abs(Fmeants_preRetcorCSF(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_preRetcorCSF).^2)
respRelativePowerPost=sum(abs(Fmeants_postRetcorCSF(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_postRetcorCSF).^2)

fcard_min_ind=ceil(fcard_min/(fs/2)*l/2);
fcard_max_ind=ceil(fcard_max/(fs/2)*l/2);
cardRelativePowerPre=sum(abs(Fmeants_preRetcorCSF(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_preRetcorCSF).^2)
cardRelativePowerPost=sum(abs(Fmeants_postRetcorCSF(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_postRetcorCSF).^2)
