function run_spikecor(volname, maskname, mpename, outprefix, OUT_PARAM, interpname)
    
    addpath('./SPIKECOR')
    addpath('./SPIKECOR/NIFTI_tools')

    output=spikecor(volname, maskname, mpename, outprefix, OUT_PARAM, interpname);

    dlmwrite(strcat(outprefix,'_censor_vol.csv'),output.censor_vol);
    dlmwrite(strcat(outprefix,'_censor_slc.csv'),output.censor_slc);

    
