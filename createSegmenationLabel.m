%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [label, frames] = createSegmenationLabel(image)

[isEndo, isOVD, frames] = segmentationDecision(image);

imshow(image)

if isEndo && ~isOVD % case ONLY ENDOTHELIUM
    label = 1; %assuming ENDOthlium and EPIThelium
    %TODO: Put frame for ENDO here and return as value
    roi = drawrectangle;
elseif isEndo && isOVD % case BOTH
    label = 2; %assuming all 3 layers
    %TODO: Put frame for OVD here and return as value
    roi = drawrectangle;
else
    label = 0;
    disp("None of the layers of interest are visible");
    return;
end

close all

end