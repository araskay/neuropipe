% function version of respbiopac2resp1d.m

% convert biopac respiration .mat file to .resp.1d (consistent with the
% output of prepphysio (.resp.1d file) run on Siemens respiration file (.resp)

function respbiopac2resp1d(infile,outfile)

% infile is biopac mat file, e.g., 7130_20140312_02.mat
% outfile should be a .resp.1D file, e.g., 7130_20140312_02.resp.1D

load(infile);

for i=1:size(labels,1)
    if labels(i,1:4)=='TRIG'
        TrigInd=i;
    elseif labels(i,1:6)=='TSD221'
        dataInd=i;
    elseif labels(i,1:7)=='RSP100C' % ran into situations in which this label was used7
        dataInd=i;
    end
end

Triger=data(:,TrigInd);

[r, c]=find(Triger==5);
[rdif, cdif]=find((r-circshift(r,1))>1); % it is possible to have multiple
% trigers besides each other. find non-adjacent trigers. use the distance
% as one TR interval (tr_int)
tr_int=r(rdif(2))-r(rdif(1));

rsp=downsample(data(r(1)-tr_int:r(end),dataInd),4);

save(outfile,'rsp','-ascii')