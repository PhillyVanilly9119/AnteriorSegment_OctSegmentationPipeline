%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [mask] = intSelectedPointsOnMask(pts, imgWidth, imgHeight)

%Precalculations
mask = zeros(imgHeight, imgWidth);
width = 1:imgWidth;
startP = min(pts(1,:));
endP = max(pts(1,:));

%Interpolate continuous function in valid range
fct(2,:) = round(interp1(pts(1,:), pts(2,:), linspace(startP, endP, length(startP:endP)), 'spline'));
fct(1,:) = linspace(startP, endP, length(startP:endP));
endGraph = startP + length(fct);
c = 0;
%write continuous function in mask [0:imgWidth]
for i = 1:length(width)
    if i < startP %graph at image boarder if i<start
        mask(imgHeight, i) = 1;
    elseif i >= (endGraph)%graph at image boarder if i>len(fct)+start
        mask(imgHeight, i) = 1;
    else %else map function in mask
        c = c + 1;
        mask(fct(2,c), i) = 1;
    end
end

end