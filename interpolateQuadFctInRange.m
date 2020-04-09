%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [curve] = interpolateQuadFctInRange(pts, length)

curve = zeros(length, 1);

pts = round(pts);
p = polyfit(pts(1,:), pts(2,:), 2);
fit = round( polyval(p, (min(pts(1,:)):max(pts(1,:))) ) );

for i = 1:length
    if all(i >= min(pts(1,:)) & i <= max(pts(1,:)))
        curve(i) = fit(i-(min(pts(1,:)))+1);
    else
        curve(i) = 0;
    end
end

end