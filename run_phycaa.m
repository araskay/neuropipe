function run_phycaa(bold,brainmask,TR,out_prefix)
    
    input_cell={bold};
    dataInfo.TR=TR;
    dataInfo.make_output=1;
    run_PHYCAA_plus(input_cell, brainmask, [], [], dataInfo, out_prefix, 2);