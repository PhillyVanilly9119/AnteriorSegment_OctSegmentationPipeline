%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [curve] = getCurves(mask, numLayers)

maskSize = size(mask);
curve = zeros(maskSize(2), numLayers);

for ii = 1:maskSize(2)
    [c,~] = find(mask(:,ii),255);
    if ~isempty(c) && length(c) == 1
        curve(ii,1) = c;
    elseif ~isempty(c) && length(c) == 2
        curve(ii,1) = min(c);
        curve(ii,2) = max(c);
    elseif ~isempty(c) && length(c) == 3
        curve(ii,1) = min(c);
        curve(ii,2) = min(max(c,2));
        curve(ii,3) = max(max(c,2));
    else
        continue
    end
end

end