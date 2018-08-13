function run_phycaa(bold,brainmask,TR,out_prefix)
    
    addpath('/home2/mkayvanrad/code/phycaa_plus_2014_09_11')
    addpath('/home2/mkayvanrad/code/phycaa_plus_2014_09_11/NIFTI_tools')
    addpath('/home2/mkayvanrad/code/phycaa_plus_2014_09_11/extra_CAA_scripts')

    input_cell={bold};
    dataInfo.TR=TR;
    dataInfo.make_output=1;

    run_PHYCAA_plus(input_cell, brainmask, [], [], dataInfo, 2, out_prefix);
