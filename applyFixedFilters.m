%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [filtered] = applyFixedFilters(vol)

% Denoise with subtraction of 75% percentile values and then apply
% openinng and closing
sz = size(vol);
filtered = zeros(sz(1), sz(2), sz(3));

for i = 1:sz(3)
    tmpImg = denoiseBScan(single(vol(:,:,i)), 75);
    filtered(:,:,i) = filterImageNoise(tmpImg, 'openAndClose', 5);
end
% Add additional filtering if neccesssary

end