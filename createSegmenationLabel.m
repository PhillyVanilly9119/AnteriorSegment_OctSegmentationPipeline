%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [label, frames] = createSegmenationLabel(image)

[isEndo, isOVD] = segmentationDecision(image);

imshow(image)

if isEndo && ~isOVD % case ONLY ENDOTHELIUM
    label = 1; %assuming ENDOthlium and EPIThelium
    %TODO: Put frame for ENDO here and return as value
    title('Please select area in which the Endothelium is clearly visible')
    roi = drawrectangle;
    frames(:,1) = [roi.Position(1), roi.Position(3)]; %?
elseif isEndo && isOVD % case BOTH
    label = 2; %assuming all 3 layers
    %TODO: Put frame for OVD here and return as value
    title('Please select area in which the Endothelium is clearly visible')
    roi = drawrectangle;
    frames(:,1) = [roi.Position(1), roi.Position(3)]; %?
    title('Please select area in which the OVD is clearly visible')
    roi = drawrectangle;
    frames(:,2) = [roi.Position(2), roi.Position(4)]; %?
else
    label = 0;
    disp("None of the layers of interest are visible");
    return;
end

close all

end