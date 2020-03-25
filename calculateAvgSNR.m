%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright: 
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [octSNR, octSNDDb] = calculateAvgSNR(octDataCube)
    sz = size(octDataCube);
    for i = 1:sz(3)
        snr(i) = calcSliceSnr(octDataCube(:,:,i0));
    end

    octSNR = mean(snr);
    octSNDDb = 20 * log10(octSNR);
    
end

function [snrBScan] = calcSliceSnr(bScan)
 
end