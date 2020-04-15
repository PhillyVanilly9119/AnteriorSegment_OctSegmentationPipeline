%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [denoisedBScan] = denoiseBScan(bScan, percentile)

% sz = size(bScan);
% onePercent = round(sz(1)*sz(2)/100);
% calculated noise on basis of lowest pixel-values
% noise = mean(bScan(bScan < mink(bScan, onePercent*percentile)));
noise = percentile;

denoisedBScan = bScan-noise; 
denoisedBScan(denoisedBScan < 0) = 0;
% fac = 255/(max(max(denoisedBScan)));
% denoisedBScan = fac .* denoisedBScan; 

end