% this code is based on physspectra.m
% this code reads mean time series of retroicor, compcor, retcomp, compret, and nophyscor
% over the network (e.g., motor
% network in the case of current fast EPI data set) and plots their power
% spectra. It also calculates and compares relative (i.e., normalized)
% power in the cardiac pulsation and respiration bands
% and saves the results into csv files. The code uses the
% frequency bands identified manually on the cardiac pulsation and
% respiration signals using power_spectra.m. Unlike physspectra.m, this
% version gets a centre (peak) frequency and calculates power over an
% interval around the centre. This eliminates variations in relative
% (normalized) power due to different interval lengths for different
% subjects (which I just realized was an issue with the previous version)
% in this version, all powers are normalized to the retroicor power on a
% per subject basis


basepath='/u1/work/hpc3820/data/healthyvolunteer/processed/physcor/';
ndiscard=10;
TR=0.380; % seconds (for current fast EPI data)


%% compute relative powers
% read the following frequencies on the resp and puls frequency specra

fin=fopen('/home/hpc3820/data/healthyvolunteer/physio/physio.csv');
fcardout=fopen('/u1/work/hpc3820/data/healthyvolunteer/processed/physcor/cardPowerSpectra.csv','w');
frespout=fopen('/u1/work/hpc3820/data/healthyvolunteer/processed/physcor/respPowerSpectra.csv','w');
flowout=fopen('/u1/work/hpc3820/data/healthyvolunteer/processed/physcor/lowPowerSpectra.csv','w');

% read the header
h=textscan(fin,'%s%s%s%s%s',1,'delimiter',',');

% read the rest
phys=textscan(fin,'%s%s%s%f%f','delimiter',',');

fprintf(fcardout,'Subject,ret,comp,retcomp,compret,nophyscor\n');
fprintf(frespout,'Subject,ret,comp,retcomp,compret,nophyscor\n');
fprintf(flowout,'Subject,ret,comp,retcomp,compret,nophyscor\n');

n=length(phys{1});

for i=1:n
    
    subject=cell2mat(phys{1}(i));
    
    retfile=strcat(basepath,subject,'/fepi/fepi_ret_slicetimer_mcflirt_fsl_motion_outliers_brainExtractAFNI_ssmooth_3dFourier_retroicor_meants_net.txt');
    compfile=strcat(basepath,subject,'/fepi/fepi_comp_slicetimer_mcflirt_fsl_motion_outliers_brainExtractAFNI_ssmooth_3dFourier_tcompcor_meants_net.txt');
    retcompfile=strcat(basepath,subject,'/fepi/fepi_retcomp_slicetimer_mcflirt_fsl_motion_outliers_brainExtractAFNI_ssmooth_3dFourier_retroicor_tcompcor_meants_net.txt');
    compretfile=strcat(basepath,subject,'/fepi/fepi_compret_slicetimer_mcflirt_fsl_motion_outliers_brainExtractAFNI_ssmooth_3dFourier_tcompcor_retroicor_meants_net.txt');
    nophyscorfile=strcat(basepath,subject,'/fepi/fepi_nophyscor_slicetimer_mcflirt_fsl_motion_outliers_brainExtractAFNI_ssmooth_3dFourier_meants_net.txt');
    lpffile=strcat(basepath,subject,'/fepi/fepi_lpf_slicetimer_mcflirt_fsl_motion_outliers_brainExtractAFNI_ssmooth_3dFourier_3dFourier_meants_net.txt');
    

    %% read mean time series
    meants_ret_fid=fopen(retfile);
    meants_ret=fscanf(meants_ret_fid,'%f');

    meants_comp_fid=fopen(compfile);
    meants_comp=fscanf(meants_comp_fid,'%f');
    
    meants_retcomp_fid=fopen(retcompfile);
    meants_retcomp=fscanf(meants_retcomp_fid,'%f');
    
    meants_compret_fid=fopen(compretfile);
    meants_compret=fscanf(meants_compret_fid,'%f');
    
    meants_nophyscor_fid=fopen(nophyscorfile);
    meants_nophyscor=fscanf(meants_nophyscor_fid,'%f');                

    meants_lpf_fid=fopen(lpffile);
    meants_lpf=fscanf(meants_lpf_fid,'%f');
    
    %% discarding frames at the beginnig
    meants_ret=meants_ret(ndiscard+1:end);
    meants_comp=meants_comp(ndiscard+1:end);
    meants_retcomp=meants_retcomp(ndiscard+1:end);
    meants_compret=meants_compret(ndiscard+1:end);
    meants_nophyscor=meants_nophyscor(ndiscard+1:end);
    meants_lpf=meants_lpf(ndiscard+1:end);
    
    %% plot power specra
    % compute FFTs
    Fmeants_ret=fft(meants_ret);
    Fmeants_comp=fft(meants_comp);
    Fmeants_retcomp=fft(meants_retcomp);
    Fmeants_compret=fft(meants_compret);
    Fmeants_nophyscor=fft(meants_nophyscor);
    Fmeants_lpf=fft(meants_lpf);
    
    %% plot
    l=length(Fmeants_ret);
    fs=1/TR;
    f=fs*(0:l/2)/l;
    
    figure(i)
    %% plot power spectra 
    subplot(6,1,1)
    plot(f,2*abs(Fmeants_ret(1:l/2+1))/l)
    title('RETROICOR');
    %xlabel('Frequency (Hz)')
    ylabel('PSD (I^2/Hz)')
    ylim([0, 0.05])

    subplot(6,1,2)
    plot(f,2*abs(Fmeants_comp(1:l/2+1))/l)
    title('CompCor');
    %xlabel('Frequency (Hz)')
    ylabel('PSD (I^2/Hz)')
    ylim([0, 0.05])
    
    subplot(6,1,3)
    plot(f,2*abs(Fmeants_retcomp(1:l/2+1))/l)
    title('RET > Comp');
    %xlabel('Frequency (Hz)')
    ylabel('PSD (I^2/Hz)')
    ylim([0, 0.05])
    
    subplot(6,1,4)
    plot(f,2*abs(Fmeants_compret(1:l/2+1))/l)
    title('Comp > RET');
    %xlabel('Frequency (Hz)')
    ylabel('PSD (I^2/Hz)')
    ylim([0, 0.05])

    subplot(6,1,5)
    plot(f,2*abs(Fmeants_lpf(1:l/2+1))/l)
    title('LPF');
    %xlabel('Frequency (Hz)')
    ylabel('PSD (I^2/Hz)')
    ylim([0, 0.05])
        
    subplot(6,1,6)
    plot(f,2*abs(Fmeants_nophyscor(1:l/2+1))/l)
    title('No Phys. Cor.');
    xlabel('Frequency (Hz)')
    ylabel('PSD (I^2/Hz)')
    ylim([0, 0.05])
    
    
    inthalf=0.05;
    fresp_min=phys{5}(i)-inthalf;
    fresp_max=phys{5}(i)+inthalf;
    fcard_min=phys{4}(i)-inthalf;
    fcard_max=phys{4}(i)+inthalf;
    
    % looking at low frequency
    flow_min=0.01;
    flow_max=0.1;

    l=length(Fmeants_ret);
    fs=1/TR;

    fresp_min_ind=ceil(fresp_min/(fs/2)*l/2);
    fresp_max_ind=ceil(fresp_max/(fs/2)*l/2);
    fcard_min_ind=ceil(fcard_min/(fs/2)*l/2);
    fcard_max_ind=ceil(fcard_max/(fs/2)*l/2);
    flow_min_ind=ceil(flow_min/(fs/2)*l/2);
    flow_max_ind=ceil(flow_max/(fs/2)*l/2);
    
    respRelativePower_ret=sum(abs(Fmeants_ret(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    respRelativePower_comp=sum(abs(Fmeants_comp(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    respRelativePower_retcomp=sum(abs(Fmeants_retcomp(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    respRelativePower_compret=sum(abs(Fmeants_compret(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    respRelativePower_nophyscor=sum(abs(Fmeants_nophyscor(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    %respRelativePower_lpf=sum(abs(Fmeants_lpf(fresp_min_ind:fresp_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    
    cardRelativePower_ret=sum(abs(Fmeants_ret(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    cardRelativePower_comp=sum(abs(Fmeants_comp(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    cardRelativePower_retcomp=sum(abs(Fmeants_retcomp(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    cardRelativePower_compret=sum(abs(Fmeants_compret(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    cardRelativePower_nophyscor=sum(abs(Fmeants_nophyscor(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    %cardRelativePower_lpf=sum(abs(Fmeants_lpf(fcard_min_ind:fcard_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    
    lowRelativePower_ret=sum(abs(Fmeants_ret(flow_min_ind:flow_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    lowRelativePower_comp=sum(abs(Fmeants_comp(flow_min_ind:flow_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    lowRelativePower_retcomp=sum(abs(Fmeants_retcomp(flow_min_ind:flow_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    lowRelativePower_compret=sum(abs(Fmeants_compret(flow_min_ind:flow_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    lowRelativePower_nophyscor=sum(abs(Fmeants_nophyscor(flow_min_ind:flow_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    %lowRelativePower_lpf=sum(abs(Fmeants_lpf(flow_min_ind:flow_max_ind)).^2)/sum(abs(Fmeants_ret).^2);
    
    card=[cardRelativePower_ret,cardRelativePower_comp,cardRelativePower_retcomp,cardRelativePower_compret,cardRelativePower_nophyscor];
    fprintf(fcardout,'%s,',subject);
    fprintf(fcardout,'%f,%f,%f,%f,%f\n',card);

    resp=[respRelativePower_ret,respRelativePower_comp,respRelativePower_retcomp,respRelativePower_compret,respRelativePower_nophyscor];
    fprintf(frespout,'%s,',subject);
    fprintf(frespout,'%f,%f,%f,%f,%f\n',resp);
    
    low=[lowRelativePower_ret,lowRelativePower_comp,lowRelativePower_retcomp,lowRelativePower_compret,lowRelativePower_nophyscor];
    fprintf(flowout,'%s,',subject);
    fprintf(flowout,'%f,%f,%f,%f,%f\n',low);
    
end

fclose(fcardout);
fclose(frespout);
fclose(flowout);
