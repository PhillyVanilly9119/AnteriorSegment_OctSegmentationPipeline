%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [curve] = interpolateBetweenSegmentedPoints(pts, imgWitdh, imgHeight)

% pts = (2 x N) points
% where first row is pos. in imgWidth and second row is pos. in imgHeight
pts = round(pts);

heightPts = interp1(pts(1,:), pts(2,:), min(pts(1,:)):max(pts(1,:)), 'PCHIP');

%Add for loop to fill non-interpolated values with 0s, which will belater
%denote spots were no layer is drawn
curve = zeros(imgWitdh, 1);
for i = 1:imgWitdh
    if all(i >= min(pts(1,:)) & i <= max(pts(1,:)))
        curve(i) = round(heightPts(i-(min(pts(1,:)))+1));
    else
        curve(i) = 0;
    end
end

curve(curve(:) > imgHeight) = imgHeight;
curve(curve < 0) = 0;

end