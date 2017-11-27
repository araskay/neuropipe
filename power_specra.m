% use this code to manually identify cardiac pulsation and respiration
% frequency bands for each subject. Change subject, pulsfile, and respfile
% below. Run. Identify frequency bands on the plots. Save the results to physio.csv.

basephyspath='/home/hpc3820/data/healthyvolunteer/physio';
subject='10577/20140325';

TR=0.380; % seconds (for current fast EPI data)
fs_phys=50;

pulsfile=strcat(basephyspath,'/',subject,'/','8fmri102a10577.puls.1D');
respfile=strcat(basephyspath,'/',subject,'/','Biopac/10577_20140325_08.resp.1D');

puls_fid=fopen(pulsfile);
puls=fscanf(puls_fid,'%f');

resp_fid=fopen(respfile);
resp=fscanf(resp_fid,'%f');

Fpuls=fft(puls);
Fresp=fft(resp);

%% plot physiology signals
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


