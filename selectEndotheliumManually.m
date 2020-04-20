%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [pts] = selectEndotheliumManually(image)

imshow(image)
title(["Select the Endothelium boundary through clicking with the cursor"...
"Please only select unique, consecutive points"...
"When the segmentation is complete, end it with a double click"])
[x,y] = getpts;
pts(:,1) = round(x);
pts(:,2) = round(y);

close(gcf)

end
