%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [label, frames] = createSegmenationLabel(image)

[isCornea, isOVD] = segmentationDecision(image);

sz = size(image);
imagesc(image)

if isCornea && ~isOVD % case ONLY CORNEA
    label = 1; %assuming ENDOthlium and EPIThelium
    title('Please select area in which the Cornea is clearly visible')
    roi = drawrectangle;
    frames(:,1) = [round(roi.Position(1)), ...
        round(roi.Position(1) + roi.Position(3))];
    frames(:,2) = [0,0];
elseif isCornea && isOVD % case BOTH
    label = 2; %assuming all 3 layers
    %TODO: Put frame for OVD here and return as value
    title('Please select area in which the Cornea is clearly visible')
    roi = drawrectangle;
    frames(:,1) = [round(roi.Position(1)), ...
        round(roi.Position(1) + roi.Position(3))];
    close all;
    pause(0.25)
    imagesc(image)
    title('Please select area in which the OVD is clearly visible')
    roi = drawrectangle;
    frames(:,2) = [round(roi.Position(1)), ...
        round(roi.Position(1) + roi.Position(3))];
else
    label = 0;
    frames = zeros(2,2);
    disp("None of the layers of interest are visible");
    
end

close all

if (min(frames(1,1)) < 1) || (max(frames(2,1)) > sz(2))
    warning("OUT OF BOUNDS ERROR: ENDOTHELIUM-margins outsinde image -> setting boundaries at image-margins");
    frames(1,1) = 1;
    frames(2,1) = sz(2);
end
if (min(frames(1,2)) < 1) || (max(frames(2,2)) > sz(2))
    warning("OUT OF BOUNDS ERROR: OVD-margins outsinde image -> setting boundaries at image-margins!");
    frames(1,2) = 1;
    frames(2,2) = sz(2);
end

end