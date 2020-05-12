%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                           Auxiliary function
%                               copyright:
%       @melanie.wuest@zeiss.com & @philipp.matten@meduniwien.ac.at
%
%   Center for Medical Physics and Biomedical Engineering (Med Uni Vienna)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [curve] = resegmentLayer(image, DataStruct, text)

pts = selectPointsManually(image, text);
while numel(pts(1,:))~= numel(unique(pts(1,:)))
    disp('Points must be unique!\n')
    pts = selectPointsManually(image, text);
end
curve = interpolateBetweenSegmentedPoints(pts,...
    DataStruct.processingVolumeDims(2), ...
    DataStruct.processingVolumeDims(1));

end