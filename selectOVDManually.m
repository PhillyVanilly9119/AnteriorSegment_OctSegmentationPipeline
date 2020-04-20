%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [pts] = selectOVDManually(image)

imshow(image)
text = fprintf("Please select the OVD boundary layer with consecutive points\nOnce done, please end selection with a double click");
title(text)

[x,y] = getpts;
pts(:,1) = round(x);
pts(:,2) = round(y);

close(gcf)

end