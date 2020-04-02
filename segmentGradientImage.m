%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [segmImg] = segmentGradientImage(image)

sz = size(image);
segmImg = zeros(sz(1),sz(2));

gradImg = createGradImg(image);

for i = 1:sz(2)
    pts(:,i) = maxk(gradImg(:,i), 3); %3 because of the 3 expected layers
    %    mPts(:,i) = mink(gradImg(:,i), 3); % also 3 because I dont yet understand the gradient
end


end