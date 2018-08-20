function run_phycaa(bold,brainmask,TR,out_prefix)
    
    addpath('/home2/mkayvanrad/code/phycaa_plus_2014_09_11')
    addpath('/home2/mkayvanrad/code/phycaa_plus_2014_09_11/NIFTI_tools')
    addpath('/home2/mkayvanrad/code/phycaa_plus_2014_09_11/extra_CAA_scripts')

    input_cell={bold};
    dataInfo.TR=TR;
    dataInfo.make_output=1;

    output2 = run_PHYCAA_plus(input_cell, brainmask, [], [], dataInfo, 2, out_prefix);
    % output2 is the output of step2

    % also save noise components
    
    for i=1:size(output2.Physio_Tset,1)
        dlmwrite(strcat(out_prefix,'_noisecomp_split',int2str(i),'.csv'),output2.Physio_Tset{i})
    end
    
