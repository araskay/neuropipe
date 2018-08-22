function run_spikecor(volname, maskname, mpename, outprefix, OUT_PARAM, interpname)
    
    addpath('/global/home/hpc3820/code/pipeline/SPIKECOR')
    addpath('/global/home/hpc3820/code/pipeline/SPIKECOR/NIFTI_tools')

    output=spikecor(volname, maskname, mpename, outprefix, OUT_PARAM, interpname);

    
