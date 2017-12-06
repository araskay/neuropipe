% use this code to manually identify cardiac pulsation and respiration
% frequency bands for each subject. Put all the subjects and the correspoindin
% puls and resp files in a csv file (list_physio.csv)
% Run. Read frequency bands on the plots and (manually) enter them on physio.csv.

basephyspath='/home/mkayvanrad/data/healthyvolunteer/physio';

% file containing list of .puls.1D and resp.1D files
fin=fopen('/home/mkayvanrad/data/healthyvolunteer/physio/list_physio.csv');


TR=0.380; % seconds (for current fast EPI data)
fs_phys=50;

% read the header
phys=textscan(fin,'%s%s%s','delimiter',',');

n=length(phys{1});

for i=2:n % first row is the header
    
  
    subject=cell2mat(phys{1}(i));
    cardfile=cell2mat(phys{2}(i));
    respfile=cell2mat(phys{3}(i));


    pulsfile=strcat(basephyspath,'/',subject,'/',cardfile);
    respfile=strcat(basephyspath,'/',subject,'/',respfile);

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
    title(strcat(subject,' Respiration Freq. Spectrum'));
    xlabel('Frequency (Hz)')
    ylabel('P(f)')

    figure(12)
    l=length(Fpuls);
    f=fs_phys*(0:l/2)/l;
    maxind=ceil((1/TR)/fs_phys*l/2); % to align with BOlD spectrum
    plot(f(1:maxind),2*abs(Fpuls(1:maxind))/l)
    title(strcat(subject,' Cardiac pulsation Freq. Spectrum'));
    xlabel('Frequency (Hz)')
    ylabel('P(f)')

    pause
    
end

