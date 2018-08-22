function run_spikecor(volname, maskname, mpename, outprefix, OUT_PARAM, interpname)
    
    addpath('./SPIKECOR')
    addpath('./SPIKECOR/NIFTI_tools')

    output=spikecor(volname, maskname, mpename, outprefix, OUT_PARAM, interpname);

    
