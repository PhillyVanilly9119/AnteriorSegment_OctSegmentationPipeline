%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [intPts] = interpolateSegmentedPoints(pts, imgWitdh, imgHeigth)

% pts = (2 x N) points
% where first row is pos. in imgWidth and second row is pos. in imgHeight
pts = round(pts);
widthLen = 1:imgWitdh;
heightPts = spline(pts(1,:), pts(2,:), widthLen);
intPts(2,:) = round(heightPts);
intPts(intPts(2,:) > imgHeigth) = imgHeigth;
warning("Points were flipped! You should have started segmenting on the right!")
intPts(1,:) = flip(widthLen);
intPts(intPts(1,:) > imgWitdh) = imgWitdh;

end