%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [denoisedBScan] = denoiseAndRescaleBScan(bScan, percentile)

sz = size(bScan);
onePercent = round(sz(1)*sz(2)/100);
% calculated noise on basis of lowest pixel-values
noise = mean(bScan(bScan < mink(bScan, onePercent*percentile)));

denoisedBScan = bScan-noise; 

end
