%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [label] = createSegmenationLabel(image)

[isEndo, isOVD] = segmentationDecision(image);
if isEndo && ~isOVD % case ONLY ENDOTHELIUM
    label = 1; %assuming ENDOthlium and EPIThelium
elseif isEndo && isOVD % case BOTH
    label = 2; %assuming all 3 layers
else
    label = 0;
    disp("None of the layers of interest are visible");
    return;
end

end