%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [octSNR, octSNRDb] = calculateAvgSNR(octDataCube)

sz = size(octDataCube);
for i = 1:sz(3)
    snr(i) = calcSliceSnr(octDataCube(:,:,i));
end

octSNR = mean(snr);
octSNRDb = 20 * log10(octSNR);

end


function [snrBScan] = calcSliceSnr(bScan)

tmp = ((double(max(bScan))- mean(bScan)).^2) ./ std(double(bScan));
snrBScan = mean(tmp);

end