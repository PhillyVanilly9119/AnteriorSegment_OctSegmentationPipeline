%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [denoisedBScan] = denoiseAndRescaleBScan(bScan, scaleFac)

sz = size(bScan);
% calculated noise on basis of 1% of lowest values in image
noise = mean(bScan(bScan < mink(bScan, round(sz(1)*sz(2)/100))));
denoisedBScan = uint8((255/scaleFac) .* (bScan-noise)); 

end
