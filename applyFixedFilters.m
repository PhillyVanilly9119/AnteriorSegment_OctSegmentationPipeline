%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [filtered] = applyFixedFilters(vol)

% Denoise with subtraction of high percentile of GVs and then apply
% openinng and closing (morphological filtering)

sz = size(vol);
filtered = zeros(sz(1), sz(2), sz(3));

for i = 1:sz(3)
    tmpImg = denoiseAndRescaleBScan(single(vol(:,:,i)), 90); % rescale based on histo-values (coarse)
    filtered(:,:,i) = filterImageNoise(tmpImg, 'openAndClose', 6); % denoise (coarse);
end

end